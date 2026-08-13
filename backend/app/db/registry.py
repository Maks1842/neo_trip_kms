"""Единственная точка импорта всех ORM-моделей.

Нужен Alembic (иначе autogenerate не увидит часть таблиц) и тестам. Приложению
в рантайме не требуется.

Список явный, а не собранный автоматически через pkgutil: автоимпорт не проверяется
mypy и молча проглатывает опечатку в имени модуля — как раз тот случай, когда ошибка
обнаружится потерянной таблицей в проде.
"""

from app.audit.models import AuditLog
from app.auth.models import RefreshToken
from app.clients.models import Client, ClientContact
from app.communications.models import CallLog, Comment, Message
from app.companies.models import Company
from app.db.base import Base
from app.deals.models import Deal, DealItem, Tourist
from app.documents.models import Attachment, Document
from app.leads.models import Lead
from app.payments.models import Payment
from app.reference.accommodations.models import (
    Accommodation,
    AccommodationNote,
    AccommodationProgram,
)
from app.reference.cities.models import City
from app.reference.countries.models import Country
from app.reference.currencies.models import Currency
from app.reference.deal_stages.models import DealStage
from app.reference.document_templates.models import DocumentTemplate
from app.reference.partners.models import Partner
from app.reference.tariff_entries.models import TariffEntry
from app.roles.models import Role
from app.tasks.models import Task
from app.users.models import User

metadata = Base.metadata

__all__ = [
    "Accommodation",
    "AccommodationNote",
    "AccommodationProgram",
    "Attachment",
    "AuditLog",
    "Base",
    "CallLog",
    "City",
    "Client",
    "ClientContact",
    "Comment",
    "Company",
    "Country",
    "Currency",
    "Deal",
    "DealItem",
    "DealStage",
    "Document",
    "DocumentTemplate",
    "Lead",
    "Message",
    "Partner",
    "Payment",
    "RefreshToken",
    "Role",
    "TariffEntry",
    "Task",
    "Tourist",
    "User",
    "metadata",
]
