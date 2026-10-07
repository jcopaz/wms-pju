# =============================================================================
# VIA WMS - ui/pages/dashboard.py
# Painel com KPIs e graficos (analise de dados).
# =============================================================================

from __future__ import annotations

import streamlit as st

from core.database import get_session
from services import analytics_service
from ui.theme import cabecalho


def render() -> None:
    cabecalho("Dashboard")

    try:
        with get_session() as db:
            kpis = analytics_service.kpis_gerais(db)
            movs = analytics_service.movimentos_por_dia(db, dias=30)
            top = analytics_service.top_materiais_consumidos(db, dias=30)
            saldo_dep = analytics_service.saldo_por_deposito(db)
    except Exception as exc:
        st.warning(
            "Banco ainda nao configurado ou vazio. "
            "Configure o .env e rode a carga inicial.\n\n"
            f"Detalhe: {exc}"
        )
        return

    # region KPIs
    c1, c2 = st.columns(2)
    c1.metric("Materiais", kpis["materiais"])
    c2.metric("Saldo total", f"{kpis['saldo_total']:.0f}")
    c3, c4 = st.columns(2)
    c3.metric("Movimentos hoje", kpis["movimentos_hoje"])
    c4.metric("Baixas pendentes SAP", kpis["baixas_pendentes"])
    # endregion

    st.divider()

    # region Grafico: movimentos por dia
    st.subheader("Movimentos (últimos 30 dias)")
    if not movs.empty:
        pivot = movs.pivot_table(
            index="dia", columns="direcao", values="qtd", fill_value=0
        )
        st.bar_chart(pivot)
    else:
        st.caption("Sem movimentos no período.")
    # endregion

    # region Top materiais + saldo por deposito
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Top consumidos")
        st.dataframe(top, hide_index=True, use_container_width=True)
    with col_b:
        st.subheader("Saldo por depósito")
        st.dataframe(saldo_dep, hide_index=True, use_container_width=True)
    # endregion
