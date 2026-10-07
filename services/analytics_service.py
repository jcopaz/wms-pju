# =============================================================================
# VIA WMS - services/analytics_service.py
# Consultas prontas para o Dashboard (KPIs e graficos).
# Retorna DataFrames do pandas, faceis de jogar em st.metric / st.bar_chart.
# =============================================================================

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.enums import MovementDirection, SAPIntegrationStatus
from models.materials import Material
from models.movements import StockMovement, StockMovementItem
from models.sap_integration import SAPPosting
from models.stock import StockBalance


# region SESSAO 1 - KPIs DE TOPO (cartoes)
def kpis_gerais(db: Session) -> dict:
    total_materiais = db.execute(
        select(func.count(Material.id))
    ).scalar_one()

    total_saldo = db.execute(
        select(func.coalesce(func.sum(StockBalance.quantity), 0))
    ).scalar_one()

    baixas_pendentes = db.execute(
        select(func.count(SAPPosting.id)).where(
            SAPPosting.status == SAPIntegrationStatus.PENDENTE
        )
    ).scalar_one()

    hoje = datetime.now(timezone.utc).date()
    movs_hoje = db.execute(
        select(func.count(StockMovement.id)).where(
            func.date(StockMovement.occurred_at) == hoje
        )
    ).scalar_one()

    return {
        "materiais": int(total_materiais or 0),
        "saldo_total": float(total_saldo or 0),
        "baixas_pendentes": int(baixas_pendentes or 0),
        "movimentos_hoje": int(movs_hoje or 0),
    }
# endregion


# region SESSAO 2 - MOVIMENTOS POR DIA (grafico de linha)
def movimentos_por_dia(db: Session, dias: int = 30) -> pd.DataFrame:
    inicio = datetime.now(timezone.utc) - timedelta(days=dias)
    stmt = (
        select(
            func.date(StockMovement.occurred_at).label("dia"),
            StockMovement.direction,
            func.count(StockMovement.id).label("qtd"),
        )
        .where(StockMovement.occurred_at >= inicio)
        .group_by(func.date(StockMovement.occurred_at), StockMovement.direction)
        .order_by(func.date(StockMovement.occurred_at))
    )
    rows = db.execute(stmt).all()
    return pd.DataFrame(
        [{"dia": r.dia, "direcao": r.direction.value, "qtd": r.qtd} for r in rows]
    )
# endregion


# region SESSAO 3 - TOP MATERIAIS CONSUMIDOS
def top_materiais_consumidos(db: Session, dias: int = 30, top: int = 10) -> pd.DataFrame:
    inicio = datetime.now(timezone.utc) - timedelta(days=dias)
    stmt = (
        select(
            Material.sap_material_number.label("material"),
            Material.description.label("descricao"),
            func.sum(StockMovementItem.quantity).label("quantidade"),
        )
        .join(StockMovement, StockMovement.id == StockMovementItem.movement_id)
        .join(Material, Material.id == StockMovementItem.material_id)
        .where(
            StockMovement.direction == MovementDirection.OUTBOUND,
            StockMovement.occurred_at >= inicio,
        )
        .group_by(Material.sap_material_number, Material.description)
        .order_by(func.sum(StockMovementItem.quantity).desc())
        .limit(top)
    )
    rows = db.execute(stmt).all()
    return pd.DataFrame(
        [
            {"material": r.material, "descricao": r.descricao,
             "quantidade": float(r.quantidade or 0)}
            for r in rows
        ]
    )
# endregion


# region SESSAO 4 - SALDO POR DEPOSITO
def saldo_por_deposito(db: Session) -> pd.DataFrame:
    from models.organization import Warehouse

    stmt = (
        select(
            Warehouse.name.label("deposito"),
            func.coalesce(func.sum(StockBalance.quantity), 0).label("saldo"),
        )
        .join(Warehouse, Warehouse.id == StockBalance.warehouse_id)
        .group_by(Warehouse.name)
        .order_by(func.sum(StockBalance.quantity).desc())
    )
    rows = db.execute(stmt).all()
    return pd.DataFrame(
        [{"deposito": r.deposito, "saldo": float(r.saldo or 0)} for r in rows]
    )
# endregion
