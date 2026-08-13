# Развёртывание в продакшене

Инструкция на будущее — когда проект будет готов к промышленной эксплуатации.
Описаны два варианта: раздельные сервисы (рекомендуемый) и всё в одном контейнере.

---

## Вариант 1. Раздельные контейнеры (рекомендуется)

Backend, frontend и база — отдельные сервисы. Их можно перезапускать и масштабировать
независимо, а статику раздаёт nginx, а не Python-процесс.

### Подготовка

```bash
cd /path/to/neo_trip_kms
cp .env.example .env
```

Обязательно изменить в `.env`:

| Переменная | Значение |
|---|---|
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `JWT_SECRET_KEY` | длинная случайная строка, своя для каждой среды |
| `POSTGRES_PASSWORD` | стойкий пароль |
| `FIRST_ADMIN_PASSWORD` | стойкий пароль |
| `CORS_ORIGINS` | реальный домен: `["https://crm.example.com"]` |

Генерация секрета:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Запуск

```bash
docker compose --profile prod build
docker compose up -d db

# Миграции — отдельный осознанный шаг, а не побочный эффект старта контейнера
docker compose --profile prod run --rm backend alembic upgrade head
docker compose --profile prod run --rm backend python -m scripts.seed

docker compose --profile prod up -d
```

Проверка:

```bash
curl http://localhost:8000/api/v1/health
curl -I http://localhost/
```

### Обновление версии

```bash
git pull
docker compose --profile prod build
docker compose --profile prod run --rm backend alembic upgrade head
docker compose --profile prod up -d
```

---

## Вариант 2. Всё в одном контейнере

Фронтенд собирается в статику и копируется внутрь образа backend, а FastAPI раздаёт её
сам. Nginx не нужен.

**Когда подходит:** одна небольшая инсталляция, немного пользователей, приоритет —
простота эксплуатации.

**Ограничения:**
- фронтенд и бэкенд масштабируются только вместе;
- статику раздаёт Python-процесс, а не специализированный сервер;
- пересборка образа нужна при любом изменении фронтенда.

### Dockerfile

Создать `Dockerfile.allinone` в корне репозитория:

```dockerfile
# ---------- Сборка фронтенда ----------
FROM node:22-alpine AS frontend

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Приложение и API отдаются одним origin, поэтому базовый путь относительный
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build

# ---------- Зависимости бэкенда ----------
FROM python:3.13-slim AS backend-deps

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---------- Итоговый образ ----------
FROM python:3.13-slim AS runtime

RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1

COPY --from=backend-deps --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app backend/app ./app
COPY --chown=app:app backend/alembic ./alembic
COPY --chown=app:app backend/scripts ./scripts
COPY --chown=app:app backend/alembic.ini ./
COPY --from=frontend --chown=app:app /frontend/dist ./static

USER app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Раздача статики из FastAPI

В `backend/app/main.py`, в конце `create_app()`, добавить:

```python
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    application.mount(
        "/assets",
        StaticFiles(directory=static_dir / "assets"),
        name="assets",
    )

    @application.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> FileResponse:
        """Отдаёт index.html на любой клиентский маршрут.

        Обработчик регистрируется последним, поэтому маршруты API он не перехватывает.
        Без него прямой переход по ссылке вида /app/reference/countries давал бы 404.
        """
        return FileResponse(static_dir / "index.html")
```

### Сборка и запуск

```bash
docker build -f Dockerfile.allinone -t neo-trip:latest .

docker network create neo_trip_net

docker run -d --name neo_trip_db --network neo_trip_net \
  -e POSTGRES_DB=neo_trip \
  -e POSTGRES_USER=neo_trip \
  -e POSTGRES_PASSWORD='СТОЙКИЙ_ПАРОЛЬ' \
  -v neo_trip_pgdata:/var/lib/postgresql \
  postgres:18-alpine

# Порядок обязателен: сначала схема, потом первичные данные, потом приложение
docker run --rm --network neo_trip_net --env-file .env \
  -e POSTGRES_HOST=neo_trip_db neo-trip:latest alembic upgrade head

docker run --rm --network neo_trip_net --env-file .env \
  -e POSTGRES_HOST=neo_trip_db neo-trip:latest python -m scripts.seed

docker run -d --name neo_trip_app --network neo_trip_net --env-file .env \
  -e POSTGRES_HOST=neo_trip_db -p 8000:8000 neo-trip:latest
```

Приложение и API доступны на одном порту: интерфейс — `http://localhost:8000/`,
документация — `http://localhost:8000/docs`.

---

## Обязательные требования безопасности

1. **Свой `JWT_SECRET_KEY` в каждой среде.** С общим секретом токен из тестового
   контура подойдёт к продакшену.
2. **Смена пароля администратора сразу после первого входа.**
3. **`APP_ENV=production` и `DEBUG=false`** — иначе клиенту уйдут детали внутренних
   ошибок.
4. **HTTPS обязателен.** Токены передаются в заголовке Authorization; по HTTP их
   перехватит любой промежуточный узел. Сертификаты — через reverse proxy
   (Caddy, Traefik, nginx с certbot).
5. **Порт базы не публиковать наружу.** В compose-варианте база доступна только
   внутри сети контейнеров.
6. **Пароли и секреты не хранить в git** — только в `.env` на сервере или в хранилище
   секретов.

---

## Резервное копирование

```bash
# Ежедневная копия
docker exec neo_trip_db pg_dump -U neo_trip -Fc neo_trip > backup_$(date +%F).dump

# Восстановление
cat backup_2026-08-13.dump | docker exec -i neo_trip_db pg_restore -U neo_trip -d neo_trip --clean
```

Копию стоит проверять восстановлением на отдельной базе: непроверенная резервная
копия — это предположение, а не гарантия.

---

## Что стоит добавить перед реальной эксплуатацией

Ниже — то, чего в проекте сейчас нет и что понадобится при промышленной нагрузке:

- сбор логов и мониторинг (health-проверки уже есть: `/api/v1/health`, `/api/v1/health/db`);
- ограничение частоты запросов к `/auth/login` — защита от подбора паролей;
- фоновая очистка просроченных refresh-токенов;
- отслеживание ошибок (Sentry или аналог);
- автоматические тесты интеграции с базой в конвейере сборки.
