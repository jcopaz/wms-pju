# =============================================================================
# VIA WMS - ui/pages/exportar_sap.py
# Tela para gerar o Excel PADRONIZADO de baixa e enviar ao SAP.
# =============================================================================

from __future__ import annotations

import streamlit as st

from core.database import get_session
from services import sap_export_service
from ui.theme import cabecalho


def render() -> None:
    cabecalho("Exportar baixa para o SAP")
    st.caption("Gera um Excel padronizado com todas as saídas pendentes de "
               "baixa, no layout esperado pelo SAP/MIGO.")

    if st.button("📤 Gerar Excel de baixa"):
        with get_session() as db:
            conteudo, nome, postings = sap_export_service.gerar_excel_baixa(db)
            if not postings:
                st.info("Não há baixas pendentes no momento.")
                return
            # Marca como exportado para nao gerar em duplicidade
            lote = sap_export_service.marcar_exportado(db, postings)

        st.success(f"{len(postings)} linha(s) exportada(s). Lote: {lote}")
        st.download_button(
            "⬇️ Baixar arquivo",
            data=conteudo,
            file_name=nome,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.caption("Após efetuar a baixa no SAP, confirme o documento de "
                   "material na tela de conciliação para fechar o ciclo.")
