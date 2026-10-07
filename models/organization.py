# =============================================================================
# VIA WMS - models/organization.py
# Estrutura organizacional, usuarios, perfis, depositos e enderecos fisicos.
# =============================================================================

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import (
    AuditUserMixin,
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


# region SESSAO 1 - UNIDADE ORGANIZACIONAL (Coordenacoes / GG)
class OrganizationUnit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "organization_units"

    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organization_units.id")
    )
    parent: Mapped[Optional["OrganizationUnit"]] = relationship(
        remote_side="OrganizationUnit.id"
    )
# endregion


# region SESSAO 2 - USUARIOS
class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150))
    registration_number: Mapped[Optional[str]] = mapped_column(String(30))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    organization_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organization_units.id")
    )
# endregion


# region SESSAO 3 - PERFIS (papeis) E VINCULO USUARIO x PERFIL
class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class UserRole(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id")
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "role_id", "warehouse_id", name="uq_user_role_wh"
        ),
    )
# endregion


# region SESSAO 4 - ESTRUTURA SAP (Centro e Deposito)
class SAPPlant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sap_plants"

    code: Mapped[str] = mapped_column(String(4), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)


class SAPStorageLocation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sap_storage_locations"

    plant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sap_plants.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(4), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    plant: Mapped["SAPPlant"] = relationship()

    __table_args__ = (
        UniqueConstraint("plant_id", "code", name="uq_sap_stloc"),
    )
# endregion


# region SESSAO 5 - DEPOSITO LOCAL DO WMS
class Warehouse(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "warehouses"

    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    organization_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organization_units.id"), nullable=False
    )
    # Vinculo com o deposito SAP correspondente (chave da conciliacao)
    sap_storage_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sap_storage_locations.id")
    )
    latitude: Mapped[Optional[float]] = mapped_column()
    longitude: Mapped[Optional[float]] = mapped_column()
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
# endregion


# region SESSAO 6 - ENDERECO FISICO (prateleira/rua/posicao)
class StorageLocation(Base, UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin):
    __tablename__ = "storage_locations"

    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("storage_locations.id")
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_type: Mapped[str] = mapped_column(String(30), default="ESTOQUE")
    barcode: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    warehouse: Mapped["Warehouse"] = relationship()

    __table_args__ = (
        UniqueConstraint("warehouse_id", "code", name="uq_stloc_wh_code"),
    )
# endregion
