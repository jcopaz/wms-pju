# =============================================================================
# VIA WMS - models/materials.py
# Cadastro de materiais (espelho do mestre SAP), unidades, lotes e series.
# =============================================================================

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import AuditUserMixin, Base, TimestampMixin, UUIDPrimaryKeyMixin
from models.enums import MaterialControlType


# region SESSAO 1 - UNIDADE DE MEDIDA
class UnitOfMeasure(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "units_of_measure"

    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
# endregion


# region SESSAO 2 - MATERIAL (MATNR do SAP)
class Material(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "materials"

    # Codigo do material no SAP (MATNR) - chave de sincronizacao
    sap_material_number: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    material_group: Mapped[Optional[str]] = mapped_column(String(30))
    material_type: Mapped[Optional[str]] = mapped_column(String(20))
    base_uom_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("units_of_measure.id"), nullable=False
    )
    control_type: Mapped[MaterialControlType] = mapped_column(
        Enum(MaterialControlType), default=MaterialControlType.QUANTITY
    )
    batch_managed: Mapped[bool] = mapped_column(Boolean, default=False)
    serial_managed: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sap_last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
# endregion


# region SESSAO 3 - LOTE
class MaterialBatch(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "material_batches"

    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False
    )
    batch_number: Mapped[str] = mapped_column(String(50), nullable=False)
    manufacturing_date: Mapped[Optional[date]] = mapped_column(Date)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date)

    __table_args__ = (
        UniqueConstraint("material_id", "batch_number", name="uq_material_batch"),
    )
# endregion


# region SESSAO 4 - NUMERO DE SERIE
class MaterialSerial(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "material_serials"

    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), nullable=False
    )
    serial_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="DISPONIVEL")
# endregion
