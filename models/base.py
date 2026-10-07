# =============================================================================
# VIA WMS - models/base.py
# Classe base e "mixins" reutilizados por todas as tabelas.
# =============================================================================

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# region SESSAO 1 - BASE DECLARATIVA
class Base(DeclarativeBase):
    pass
# endregion


# region SESSAO 2 - MIXIN DE CHAVE PRIMARIA (UUID)
class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
# endregion


# region SESSAO 3 - MIXIN DE DATAS (criado/atualizado)
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
# endregion


# region SESSAO 4 - MIXIN DE AUDITORIA (quem criou/alterou)
class AuditUserMixin:
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
# endregion
