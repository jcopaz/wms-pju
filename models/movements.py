# =============================================================================
# VIA WMS - models/movements.py
# Documentos de movimentacao (cabecalho + itens). O coracao do WMS.
# Toda entrada, saida e transferencia vira um StockMovement com itens.
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
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import AuditUserMixin, Base, TimestampMixin, UUIDPrimaryKeyMixin
from models.enums import (
    DocumentStatus,
    MovementDirection,
    MovementType,
    OwnershipType,
    StockType,
)


# region SESSAO 1 - CABECALHO DO MOVIMENTO
class StockMovement(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "stock_movements"

    movement_number: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    movement_type: Mapped[MovementType] = mapped_column(
        Enum(MovementType), nullable=False
    )
    direction: Mapped[MovementDirection] = mapped_column(
        Enum(MovementDirection), nullable=False
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.RASCUNHO, nullable=False
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    # Objeto de custo / destinatario / contrato (para saidas)
    account_assignment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("account_assignments.id")
    )
    recipient_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recipients.id")
    )
    contract_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id")
    )
    operational_order_number: Mapped[Optional[str]] = mapped_column(String(50))
    railway_location: Mapped[Optional[str]] = mapped_column(String(150))
    # Geolocalizacao do registro no celular
    latitude: Mapped[Optional[float]] = mapped_column()
    longitude: Mapped[Optional[float]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Se for estorno, aponta para o movimento original
    original_movement_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_movements.id")
    )

    items: Mapped[list["StockMovementItem"]] = relationship(
        back_populates="movement", cascade="all, delete-orphan"
    )
# endregion


# region SESSAO 2 - ITEM DO MOVIMENTO
class StockMovementItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "stock_movement_items"

    movement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_movements.id"), nullable=False
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False
    )
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("material_batches.id")
    )
    source_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("storage_locations.id")
    )
    destination_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("storage_locations.id")
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    uom_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("units_of_measure.id"), nullable=False
    )
    stock_type: Mapped[StockType] = mapped_column(
        Enum(StockType), default=StockType.UNRESTRICTED, nullable=False
    )
    ownership_type: Mapped[OwnershipType] = mapped_column(
        Enum(OwnershipType), default=OwnershipType.MRS, nullable=False
    )
    contractor_ownership_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contractors.id")
    )
    unit_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    total_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))

    movement: Mapped["StockMovement"] = relationship(back_populates="items")

    __table_args__ = (
        UniqueConstraint("movement_id", "line_number", name="uq_mov_item_line"),
        CheckConstraint("quantity > 0", name="ck_mov_item_qty_positive"),
    )
# endregion
