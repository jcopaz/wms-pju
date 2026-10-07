# =============================================================================
# VIA WMS - models/sap_integration.py
# Registro de tudo que entra do SAP (import) e sai para o SAP (export/baixa).
# =============================================================================

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import AuditUserMixin, Base, TimestampMixin, UUIDPrimaryKeyMixin
from models.enums import SAPIntegrationStatus


# region SESSAO 1 - LOTE DE IMPORTACAO (Excel do SAP recebido)
class SAPImportBatch(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "sap_import_batches"

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(128))
    import_type: Mapped[str] = mapped_column(String(30), default="ESTOQUE")
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_rows: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="PROCESSADO")
    log: Mapped[Optional[dict]] = mapped_column(JSON)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
# endregion


# region SESSAO 2 - POSTAGEM/BAIXA NO SAP (export para baixa)
class SAPPosting(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "sap_postings"

    stock_movement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_movements.id"), nullable=False
    )
    status: Mapped[SAPIntegrationStatus] = mapped_column(
        Enum(SAPIntegrationStatus), default=SAPIntegrationStatus.PENDENTE, nullable=False
    )
    sap_movement_type: Mapped[str] = mapped_column(String(3), nullable=False)
    sap_material_document: Mapped[Optional[str]] = mapped_column(String(20))
    sap_fiscal_year: Mapped[Optional[str]] = mapped_column(String(4))
    sap_document_date: Mapped[Optional[date]] = mapped_column(Date)
    sap_posting_date: Mapped[Optional[date]] = mapped_column(Date)
    source_plant_code: Mapped[Optional[str]] = mapped_column(String(4))
    source_storage_location_code: Mapped[Optional[str]] = mapped_column(String(4))
    destination_plant_code: Mapped[Optional[str]] = mapped_column(String(4))
    destination_storage_location_code: Mapped[Optional[str]] = mapped_column(String(4))
    export_batch_id: Mapped[Optional[str]] = mapped_column(String(40))
    request_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    response_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    exported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reconciled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_sap_posting_doc", "sap_material_document", "sap_fiscal_year"),
    )
# endregion


# region SESSAO 3 - ANEXOS E AUDITORIA
class Attachment(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "attachments"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_hash: Mapped[Optional[str]] = mapped_column(String(128))

    __table_args__ = (Index("ix_attachment_entity", "entity_type", "entity_id"),)


class AuditLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "audit_logs"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    old_values: Mapped[Optional[dict]] = mapped_column(JSON)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_occurred_at", "occurred_at"),
    )
# endregion
