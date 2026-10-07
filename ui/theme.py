# =============================================================================
# VIA WMS - ui/theme.py
# Tema visual (mesma linha do Sentinel): cores, CSS mobile-first e cabecalho.
# =============================================================================

from __future__ import annotations

import streamlit as st

from core.config import (
    APP_NAME,
    APP_SUBTITLE,
    COR_ALERTA,
    COR_FUNDO,
    COR_NEUTRA,
    COR_PRIMARIA,
    COR_SECUNDARIA,
    COR_SUCESSO,
)


# region SESSAO 1 - CSS GLOBAL (otimizado para celular)
def aplicar_estilo() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {COR_FUNDO}; }}

        /* Botoes grandes, faceis de tocar no campo */
        .stButton > button {{
            background-color: {COR_PRIMARIA};
            color: #FFFFFF;
            border: none;
            border-radius: 12px;
            padding: 0.9rem 1.1rem;
            font-weight: 600;
            width: 100%;
            font-size: 1.05rem;
        }}
        .stButton > button:hover {{ background-color: {COR_SECUNDARIA}; color: {COR_PRIMARIA}; }}

        /* Cartoes de KPI */
        div[data-testid="stMetric"] {{
            background: #FFFFFF;
            border-radius: 14px;
            padding: 14px 16px;
            border-left: 6px solid {COR_SECUNDARIA};
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }}

        /* Cabecalho */
        .via-header {{
            background: {COR_PRIMARIA};
            color: #FFFFFF;
            padding: 14px 18px;
            border-radius: 0 0 16px 16px;
            margin: -1rem -1rem 1rem -1rem;
        }}
        .via-header h1 {{ font-size: 1.25rem; margin: 0; }}
        .via-header span {{ color: {COR_SECUNDARIA}; font-size: 0.8rem; }}

        .badge-ok {{ color: {COR_SUCESSO}; font-weight: 700; }}
        .badge-alerta {{ color: {COR_ALERTA}; font-weight: 700; }}
        .badge-neutro {{ color: {COR_NEUTRA}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
# endregion


# region SESSAO 2 - CABECALHO PADRAO
def cabecalho(subtitulo: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="via-header">
            <h1>🚆 {APP_NAME}</h1>
            <span>{subtitulo or APP_SUBTITLE}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
# endregion
