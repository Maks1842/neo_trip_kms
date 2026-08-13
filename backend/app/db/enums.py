"""Перечисления, общие для всех доменов.

Все ENUM собраны в одном файле сознательно: в PostgreSQL это глобальные объекты базы,
и половина из них используется в нескольких доменах (funnel_type — в этапах воронки и
в сделках, document_type — в шаблонах и документах). Разнесение по доменным пакетам
дало бы циклические импорты и дубли типов в БД.
"""

from enum import StrEnum

from sqlalchemy import Enum as SAEnum


def pg_enum(py_enum: type[StrEnum], name: str) -> SAEnum:
    """Создаёт PostgreSQL ENUM из Python-перечисления.

    values_callable обязателен: без него SQLAlchemy запишет в базу ИМЕНА членов
    перечисления (NEW, PROCESSING), а не их значения (new, processing).
    """
    return SAEnum(
        py_enum,
        name=name,
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
        native_enum=True,
    )


# ---------- Лиды и клиенты ----------


class LeadStatus(StrEnum):
    NEW = "new"
    PROCESSING = "processing"
    CONVERTED = "converted"
    DUPLICATE = "duplicate"
    SPAM = "spam"


class ClientContactType(StrEnum):
    PHONE = "phone"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    VK = "vk"


# ---------- Объекты размещения ----------


class AccommodationType(StrEnum):
    HOTEL = "hotel"
    SANATORIUM = "sanatorium"


class AccommodationNoteSource(StrEnum):
    MANUAL = "manual"
    NPS_PARSED = "nps_parsed"


# ---------- Сделки ----------


class FunnelType(StrEnum):
    CRUISE = "cruise"
    TOUR = "tour"
    SANATORIUM = "sanatorium"


class DealItemType(StrEnum):
    ACCOMMODATION = "accommodation"
    FLIGHT = "flight"
    TRANSFER = "transfer"
    EXCURSION = "excursion"
    OTHER = "other"


# ---------- Задачи ----------


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    OVERDUE = "overdue"


class TaskCreatedBy(StrEnum):
    SYSTEM = "system"
    MANUAL = "manual"


# ---------- Коммуникации ----------


class MessageChannel(StrEnum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    EMAIL = "email"
    CALL = "call"


class MessageDirection(StrEnum):
    IN = "in"
    OUT = "out"


# ---------- Документы ----------


class DocumentType(StrEnum):
    CONTRACT = "contract"
    INVOICE = "invoice"
    VOUCHER = "voucher"


class DocumentStatus(StrEnum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"


class AttachmentFileType(StrEnum):
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class AttachmentSource(StrEnum):
    MANUAL = "manual"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    EMAIL = "email"
    OCR = "ocr"


# ---------- Финансы ----------


class PaymentDirection(StrEnum):
    IN = "in"
    OUT = "out"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(StrEnum):
    ACQUIRING = "acquiring"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    # В исходных материалах значение называлось 1c_sync — идентификатор не может
    # начинаться с цифры, поэтому используется onec_sync.
    ONEC_SYNC = "onec_sync"


# ---------- Партнёры ----------


class PartnerType(StrEnum):
    SUB_AGENT = "sub_agent"
    REFERRAL_CLIENT = "referral_client"
    AFFILIATE = "affiliate"


# ---------- Аудит ----------


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
