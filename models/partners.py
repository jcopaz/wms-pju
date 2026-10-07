# =============================================================================
# VIA WMS - models/partners.py
# Contratadas (CNPJ), contratos, destinatarios e objetos de custo (SAP).
# =============================================================================

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import AuditUserMixin, Base, TimestampMixin, UUIDPrimaryKeyMixin
from models.enums import AccountAssignmentType, RecipientType


# region SESSAO 1 - CONTRATADA (CNPJ)
class Contractor(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "contractors"

    tax_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    legal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    trade_name: Mapped[Optional[str]] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
# endregion


# region SESSAO 2 - CONTRATO
class Contract(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "contracts"

    contractor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contractors.id"), nullable=False
    )
    contract_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(String(255))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
# endregion


# region SESSAO 3 - DESTINATARIO (quem recebe o material)
class Recipient(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "recipients"

    recipient_type: Mapped[RecipientType] = mapped_column(
        Enum(RecipientType), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    registration_number: Mapped[Optional[str]] = mapped_column(String(30))
    document_number: Mapped[Optional[str]] = mapped_column(String(30))
    contractor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contractors.id")
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
# endregion


# region SESSAO 4 - OBJETO DE CUSTO SAP (Ordem, Centro de Custo, PEP)
class AccountAssignment(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "account_assignments"

    assignment_type: Mapped[AccountAssignmentType] = mapped_column(
        Enum(AccountAssignmentType), nullable=False
    )
    sap_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    sap_plant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sap_plants.id")
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("assignment_type", "sap_code", name="uq_acc_assign"),
    )
# endregion
