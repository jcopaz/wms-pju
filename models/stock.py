# =============================================================================
# VIA WMS - models/stock.py
# Saldo de estoque por deposito/endereco/material/lote/propriedade.
# =============================================================================

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from models.enums import OwnershipType, StockType


# region SESSAO 1 - SALDO DE ESTOQUE
class StockBalance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "stock_balances"

    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("storage_locations.id"), nullable=False
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False
    )
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("material_batches.id")
    )
    stock_type: Mapped[StockType] = mapped_column(
        Enum(StockType), default=StockType.UNRESTRICTED, nullable=False
    )
    ownership_type: Mapped[OwnershipType] = mapped_column(
        Enum(OwnershipType), default=OwnershipType.MRS, nullable=False
    )
    contractor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contractors.id")
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), default=Decimal("0"), nullable=False
    )
    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), default=Decimal("0"), nullable=False
    )
    # Controle de concorrencia (evita duas baixas simultaneas errarem o saldo)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_stock_qty_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="ck_stock_reserved_non_neg"),
        Index(
            "ix_stock_lookup",
            "warehouse_id",
            "location_id",
            "material_id",
            "batch_id",
            "stock_type",
            "ownership_type",
        ),
    )

    @property
    def available_quantity(self) -> Decimal:
        """Saldo realmente disponivel para entregar (saldo - reservado)."""
        return self.quantity - self.reserved_quantity
# endregion
