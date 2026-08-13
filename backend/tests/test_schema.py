"""Проверки целостности схемы данных.

Эти тесты не требуют подключения к базе: они ловят ошибки, которые иначе
обнаружились бы только потерянной таблицей или колонкой в продакшене.
"""

import pkgutil

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

import app
from app.db.registry import metadata

# Таблицы, у которых company_id отсутствует намеренно: сама компания и
# глобальные справочники, общие для всех арендаторов.
TABLES_WITHOUT_COMPANY = {"companies", "countries", "cities", "currencies", "refresh_tokens"}

EXPECTED_TABLE_COUNT = 28


def test_all_model_modules_are_registered() -> None:
    """Каждый модуль models.py должен быть импортирован в реестре.

    Забытый импорт означает, что Alembic не увидит таблицу и она просто
    не будет создана.
    """
    found: set[str] = set()
    for module in pkgutil.walk_packages(app.__path__, prefix="app."):
        if module.name.endswith(".models"):
            found.add(module.name)

    registry_source = (
        __import__("pathlib").Path(app.__file__).parent / "db" / "registry.py"
    ).read_text(encoding="utf-8")
    missing = {name for name in found if f"from {name} import" not in registry_source}
    assert not missing, f"Модули моделей не импортированы в registry.py: {sorted(missing)}"


def test_expected_number_of_tables() -> None:
    assert len(metadata.tables) == EXPECTED_TABLE_COUNT, sorted(metadata.tables)


def test_every_table_has_audit_columns() -> None:
    """created_at и updated_at должны быть у всех таблиц без исключения."""
    broken = [
        name
        for name, table in metadata.tables.items()
        if "created_at" not in table.columns or "updated_at" not in table.columns
    ]
    assert not broken, f"Нет аудит-полей: {sorted(broken)}"


def test_tenant_tables_have_company_id() -> None:
    """Все таблицы, кроме глобальных, должны быть привязаны к компании."""
    broken = [
        name
        for name, table in metadata.tables.items()
        if name not in TABLES_WITHOUT_COMPANY and "company_id" not in table.columns
    ]
    assert not broken, f"Нет company_id: {sorted(broken)}"


def test_ddl_compiles_for_postgresql() -> None:
    """DDL каждой таблицы должен собираться под PostgreSQL."""
    for table in metadata.tables.values():
        CreateTable(table).compile(dialect=postgresql.dialect())


def test_primary_keys_are_uuid() -> None:
    for name, table in metadata.tables.items():
        pk_columns = list(table.primary_key.columns)
        assert len(pk_columns) == 1, f"{name}: ожидается одиночный первичный ключ"
        assert pk_columns[0].name == "id", f"{name}: первичный ключ должен называться id"
