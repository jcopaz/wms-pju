# =============================================================================
# VIA WMS - models/custody.py
# Custodia: material entregue temporariamente a colaborador/terceiro.
# Controla quanto foi entregue, consumido, devolvido e perdido.
# =============================================================================

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import AuditUserMixin, Base, TimestampMixin, UUIDPrimaryKeyMixin
from models.enums import CustodyStatus


# region SESSAO 1 - CABECALHO DA CUSTODIA
class MaterialCustody(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "material_custodies"

    custody_number: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipients.id"), nullable=False
    )
    contract_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id")
    )
    account_assignment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("account_assignments.id")
    )
    issue_movement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_movements.id"), nullable=False
    )
    status: Mapped[CustodyStatus] = mapped_column(
        Enum(CustodyStatus), default=CustodyStatus.ABERTA, nullable=False
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expected_return_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    items: Mapped[list["MaterialCustodyItem"]] = relationship(
        back_populates="custody", cascade="all, delete-orphan"
    )
# endregion


# region SESSAO 2 - ITEM DA CUSTODIA
class MaterialCustodyItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "material_custody_items"

    custody_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("material_custodies.id"), nullable=False
    )
    movement_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_movement_items.id"), nullable=False
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False
    )
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("material_batches.id")
    )
    issued_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    consumed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), default=Decimal("0"), nullable=False
    )
    returned_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), default=Decimal("0"), nullable=False
    )
    lost_or_damaged_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), default=Decimal("0"), nullable=False
    )

    custody: Mapped["MaterialCustody"] = relationship(back_populates="items")

    __table_args__ = (
        CheckConstraint("issued_quantity > 0", name="ck_custody_issued_pos"),
        CheckConstraint(
            "consumed_quantity + returned_quantity + lost_or_damaged_quantity "
            "<= issued_quantity",
            name="ck_custody_qty_limit",
        ),
    )

    @property
    def open_quantity(self) -> Decimal:
        """Quanto ainda esta em poder do destinatario (nao resolvido)."""
        return (
            self.issued_quantity
            - self.consumed_quantity
            - self.returned_quantity
            - self.lost_or_damaged_quantity
        )
# endregion
