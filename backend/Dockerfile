# ---------- Стадия сборки: установка зависимостей ----------
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Зависимости ставятся отдельным слоем: пока pyproject.toml и uv.lock не менялись,
# слой берётся из кэша и пересборка образа не переустанавливает пакеты.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---------- Стадия исполнения ----------
FROM python:3.13-slim AS runtime

# Непривилегированный пользователь: процесс приложения не должен работать от root.
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home app

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app scripts ./scripts
COPY --chown=app:app alembic.ini pyproject.toml ./

USER app

EXPOSE 8000

# Миграции намеренно не выполняются при старте контейнера: применение изменений
# схемы — отдельное решение оператора, а не побочный эффект перезапуска сервиса.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
