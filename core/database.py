# =============================================================================
# VIA WMS - core/database.py
# Conexao com o banco (Supabase/Postgres) via SQLAlchemy 2.
# -----------------------------------------------------------------------------
# Julio: aqui e onde o sistema "abre a porta" do banco de dados.
# Em qualquer servico, voce usa `with get_session() as db:` para trabalhar.
# =============================================================================

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings


# region SESSAO 1 - CRIACAO DO ENGINE
# -----------------------------------------------------------------------------
_engine: Engine | None = None
_SessionFactory: sessionmaker | None = None


def get_engine() -> Engine:
    """Cria (uma unica vez) a conexao com o banco."""
    global _engine
    if _engine is None:
        settings = get_settings()
        if not settings.db.is_configured:
            raise RuntimeError(
                "DATABASE_URL nao configurada. Preencha o arquivo .env "
                "com a string de conexao do Supabase."
            )
        _engine = create_engine(
            settings.db.url,
            echo=settings.db.echo,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
            pool_pre_ping=True,  # evita conexao "morta" no Supabase
            future=True,
        )
    return _engine
# endregion


# region SESSAO 2 - FABRICA DE SESSOES
# -----------------------------------------------------------------------------
def get_session_factory() -> sessionmaker:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=Session,
            future=True,
        )
    return _SessionFactory
# endregion


# region SESSAO 3 - CONTEXTO DE SESSAO (commit/rollback automatico)
# -----------------------------------------------------------------------------
@contextmanager
def get_session() -> Iterator[Session]:
    """
    Uso:
        with get_session() as db:
            db.add(objeto)
    Se der erro, faz rollback sozinho. Se der certo, faz commit sozinho.
    """
    factory = get_session_factory()
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
# endregion


# region SESSAO 4 - CRIACAO DAS TABELAS (bootstrap)
# -----------------------------------------------------------------------------
def criar_tabelas() -> None:
    """Cria todas as tabelas no banco a partir dos models. Uso unico/inicial."""
    from models.base import Base
    import models  # noqa: F401  (garante que todos os models sejam importados)

    Base.metadata.create_all(bind=get_engine())
# endregion
