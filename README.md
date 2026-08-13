# Neo Trip CRM

Ядро CRM для туристического бизнеса: справочники, авторизация и каркас разделов.

**Что уже работает:** авторизация с обновлением токенов, разграничение прав, полный CRUD
по десяти справочникам, каркас интерфейса со всеми разделами.

**Чего пока нет:** бизнес-логика сделок, лидов, клиентов, документов и платежей — модели
в базе созданы, но эндпоинты и экраны для них не реализованы. PMS, финтех и маркетплейс
в этот трек не входят.

---

## Стек

| Слой | Технологии |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0 (async), asyncpg, Alembic, Pydantic v2, uv |
| Frontend | Vue 3.5, TypeScript, Vite, Pinia, Vue Router, PrimeVue 5 (тема Aura), Tailwind 4 |
| База данных | PostgreSQL 18 в Docker |
| Качество кода | Ruff, mypy (strict), pytest — backend; ESLint, Prettier, vue-tsc — frontend |

---

## Требования

- **Docker** и **Docker Compose**
- **Python 3.13** и **[uv](https://docs.astral.sh/uv/)**
- **Node.js 22 LTS**

В этом окружении Node 22 установлен через [fnm](https://github.com/Schniz/fnm)
в `~/.local/share/fnm`. Чтобы он подхватывался в новых терминалах, добавьте в `~/.bashrc`:

```bash
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env --shell bash)"
```

Проверка: `node -v` должен показать `v22.x`.

---

## Быстрый старт

### 1. Переменные окружения

```bash
cd /home/maks/My_Projects/Python_projects/neo_trip_kms
cp .env.example .env
```

В `.env` обязательно задайте:

- `POSTGRES_PASSWORD` — пароль базы данных;
- `JWT_SECRET_KEY` — длинную случайную строку
  (`python3 -c "import secrets; print(secrets.token_urlsafe(64))"`);
- `FIRST_ADMIN_PASSWORD` — пароль первого администратора.

`.env` в репозиторий не попадает.

### 2. База данных

```bash
docker compose up -d db
docker compose ps          # статус должен быть healthy
```

База поднимается на порту **5434** (5432 и 5433 в этой системе заняты).
Порт задаётся переменной `POSTGRES_PORT`.

### 3. Backend

```bash
cd backend
uv sync                                              # установка зависимостей в .venv

uv run alembic upgrade head                          # применение миграции схемы
uv run python -m scripts.seed                        # компания, роли, администратор

uv run uvicorn app.main:app --reload
```

API доступен на `http://localhost:8000`, документация — `http://localhost:8000/docs`.

### 4. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Интерфейс: `http://localhost:5173`. Запросы к `/api` dev-сервер проксирует на backend,
поэтому настраивать CORS для разработки не требуется.

### 5. Вход

Учётные данные берутся из `.env` (`FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`).
По умолчанию — `admin@neotrip.ru`.

---

## Работа с миграциями

Схема описана моделями SQLAlchemy; миграции генерируются по ним.

```bash
cd backend

# после изменения моделей
uv run alembic revision --autogenerate -m "описание изменения"
uv run ruff format alembic/versions          # форматирование сгенерированного файла
uv run alembic upgrade head                  # применение

uv run alembic downgrade -1                  # откат на шаг назад
uv run alembic current                       # текущая ревизия
```

**Важно про взаимные ссылки.** Таблицы `leads` и `clients` ссылаются друг на друга,
поэтому их внешние ключи создаются отдельными командами `ALTER TABLE` в конце миграции.
Alembic не генерирует их автоматически — при пересоздании начальной миграции с нуля
эти две команды нужно добавить вручную (образец есть в текущей начальной миграции).

---

## Полезные команды

### Backend

```bash
uv run ruff check .            # линтер
uv run ruff format .           # форматирование
uv run mypy app                # проверка типов (strict)
uv run pytest                  # тесты
```

### Frontend

```bash
npm run lint                   # ESLint с автоисправлением
npm run type-check             # проверка типов
npm run build                  # production-сборка
npm run test                   # Vitest
```

### База данных

```bash
# подключение к базе в контейнере
docker exec -it neo_trip_db psql -U neo_trip -d neo_trip

# резервная копия и восстановление
docker exec neo_trip_db pg_dump -U neo_trip neo_trip > backup.sql
cat backup.sql | docker exec -i neo_trip_db psql -U neo_trip -d neo_trip
```

---

## Структура проекта

```
neo_trip_kms/
├── docker-compose.yml        PostgreSQL (профиль prod добавляет backend и frontend)
├── .env.example              шаблон переменных окружения
├── README.md                 этот файл
├── DEPLOY_PRODUCTION.md      развёртывание в одном контейнере
├── CLAUDE.md                 правила разработки проекта
│
├── backend/
│   ├── alembic/              миграции схемы
│   ├── scripts/seed.py       первичное наполнение базы
│   ├── tests/                тесты
│   └── app/
│       ├── core/             конфигурация, безопасность, обработка ошибок
│       ├── db/               базовый класс моделей, миксины, типы, перечисления, реестр
│       ├── common/           общий CRUD-слой, пагинация, работа с деньгами
│       ├── api/              сборка маршрутов и служебные эндпоинты
│       ├── auth/             авторизация
│       ├── reference/        справочники
│       └── …                 остальные домены (пока только модели)
│
└── frontend/src/
    ├── api/                  HTTP-клиент и клиенты ресурсов
    ├── assets/styles/        все кастомные стили проекта
    ├── components/           переиспользуемые компоненты
    ├── composables/          уведомления, состояние CRUD-экранов
    ├── layouts/              каркас приложения и страницы входа
    ├── pages/                страницы разделов
    ├── router/               маршрутизация
    ├── stores/               Pinia-сторы
    └── types/                типы обмена с API
```

---

## API

Базовый префикс — `/api/v1`. Полное описание: `http://localhost:8000/docs`.

| Группа | Эндпоинты |
|---|---|
| Служебные | `GET /health`, `GET /health/db` |
| Авторизация | `POST /auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/logout-all`, `/auth/change-password`, `GET /auth/me` |
| Роли | `GET/POST /roles`, `GET/PATCH/DELETE /roles/{id}` |
| Справочники | `/reference/{countries,cities,currencies,accommodations,accommodation-programs,tariff-entries,deal-stages,partners,document-templates}` — полный CRUD |
| Порядок этапов | `PATCH /reference/deal-stages/reorder` |

Ошибки всех видов возвращаются в едином формате:

```json
{
  "error": {
    "code": "conflict",
    "message": "Страна с такими значениями полей (code) уже существует",
    "details": [],
    "request_id": "…"
  }
}
```

### Денежные суммы

В базе суммы хранятся целыми числами в минимальных единицах валюты (копейках) — это
исключает ошибки округления и расхождения при сверке с внешними системами. В API суммы
передаются в основных единицах (рублях): `1234.56` при сохранении превращается
в `123456` и возвращается обратно без потерь. Число знаков после запятой берётся
из справочника валют.

---

## Права доступа

Права — плоский список кодов вида `<домен>.<действие>` в поле `permissions` роли.
Код `*` означает полный доступ.

Системные роли создаёт скрипт наполнения: **Администратор**, **Руководитель**,
**Менеджер**, **Бухгалтер**, **Маркетолог**. Изменять и удалять их через API нельзя.
