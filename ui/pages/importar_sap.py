# =============================================================================
# VIA WMS - ui/pages/importar_sap.py
# Tela para subir o Excel exportado do SAP e sincronizar materiais.
# =============================================================================

from __future__ import annotations

import streamlit as st

from core.database import get_session
from services import sap_import_service
from ui.theme import cabecalho


def render() -> None:
    cabecalho("Importar base do SAP")
    st.caption("Suba o Excel exportado do SAP (cadastro/estoque). O sistema "
               "atualiza os materiais automaticamente.")

    arquivo = st.file_uploader("Arquivo Excel (.xlsx)", type=["xlsx", "xls"])

    if arquivo is not None:
        # Previa das primeiras linhas para conferencia
        try:
            df = sap_import_service.ler_excel(arquivo)
            st.write("Prévia do arquivo:")
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Colunas detectadas: {list(df.columns)}")
        except Exception as exc:
            st.error(f"Não consegui ler o arquivo: {exc}")
            return

        if st.button("📥 Importar e sincronizar"):
            arquivo.seek(0)
            with get_session() as db:
                res, batch = sap_import_service.importar_estoque_sap(
                    db, arquivo, arquivo.name
                )
            st.success("Importação concluída.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Criados", res.criados)
            c2.metric("Atualizados", res.atualizados)
            c3.metric("Erros", res.erros)
            if res.mensagens:
                with st.expander("Mensagens/erros"):
                    for m in res.mensagens[:50]:
                        st.write("- ", m)
