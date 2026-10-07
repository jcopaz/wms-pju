# =============================================================================
# VIA WMS - models/inventory.py
# Inventario: campanha de contagem, contagens e recontagens.
# =============================================================================

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
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
from sqlalchemy.orm import Mapped, mapped_column

from models.base import AuditUserMixin, Base, TimestampMixin, UUIDPrimaryKeyMixin
from models.enums import InventoryStatus


# region SESSAO 1 - CAMPANHA DE INVENTARIO
class InventorySession(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "inventory_sessions"

    inventory_number: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    status: Mapped[InventoryStatus] = mapped_column(
        Enum(InventoryStatus), default=InventoryStatus.PLANEJADO, nullable=False
    )
    cutoff_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    blind_count: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
# endregion


# region SESSAO 2 - CONTAGEM
class InventoryCount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "inventory_counts"

    inventory_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_sessions.id"), nullable=False
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
    count_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    system_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    counted_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    difference_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    counted_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    counted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    adjustment_movement_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stock_movements.id")
    )
    justification: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            "inventory_session_id",
            "location_id",
            "material_id",
            "batch_id",
            "count_number",
            name="uq_inventory_count_round",
        ),
    )
# endregion
