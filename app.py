# =============================================================================
# VIA WMS - app.py  (aplicacao principal Streamlit, mobile-first)
# -----------------------------------------------------------------------------
# Julio: este e o "ponto de entrada". Ele monta o menu e chama cada tela.
# Rodar:  streamlit run app.py
# Organizacao por Sessoes, como no Sentinel.
# =============================================================================

from __future__ import annotations

import streamlit as st

from core.config import APP_NAME
from ui.theme import aplicar_estilo, cabecalho


# region SESSAO 1 - CONFIGURACAO DA PAGINA
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🚆",
    layout="centered",          # 'centered' fica melhor no celular
    initial_sidebar_state="collapsed",
)
aplicar_estilo()
# endregion


# region SESSAO 2 - LOGIN PROVISORIO (usuarios no banco; AD/Entra ID depois)
MAX_TENTATIVAS = 5


def tela_login() -> bool:
    """Mostra o formulario de login e valida no banco (services/auth_service)."""
    from core.database import get_session
    from services import auth_service

    cabecalho("Acesso ao sistema")
    tentativas = st.session_state.get("tentativas_login", 0)
    if tentativas >= MAX_TENTATIVAS:
        st.error("Muitas tentativas erradas. Feche o navegador e tente de novo mais tarde.")
        return False

    with st.form("login"):
        login = st.text_input("Usuario (matricula)")
        senha = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar")
    if ok and login and senha:
        with get_session() as db:
            usuario = auth_service.autenticar(db, login, senha)
        if usuario is None:
            st.session_state["tentativas_login"] = tentativas + 1
            st.error("Usuario ou senha invalidos.")
        else:
            st.session_state.pop("tentativas_login", None)
            st.session_state["user"] = {
                "id": usuario.id, "login": usuario.login, "name": usuario.name,
            }
            st.rerun()
    return "user" in st.session_state
# endregion


# region SESSAO 3 - MENU PRINCIPAL
MENU = {
    "🏠 Dashboard": "dashboard",
    "⬇️ Entrada": "entrada",
    "⬆️ Saída": "saida",
    "🔁 Transferência": "transferencia",
    "📦 Inventário": "inventario",
    "📥 Importar SAP": "importar_sap",
    "📤 Exportar Baixa SAP": "exportar_sap",
}


def roteador(destino: str) -> None:
    if destino == "dashboard":
        from ui.pages import dashboard
        dashboard.render()
    elif destino == "entrada":
        from ui.pages import entrada
        entrada.render()
    elif destino == "saida":
        from ui.pages import saida
        saida.render()
    elif destino == "transferencia":
        from ui.pages import transferencia
        transferencia.render()
    elif destino == "inventario":
        from ui.pages import inventario
        inventario.render()
    elif destino == "importar_sap":
        from ui.pages import importar_sap
        importar_sap.render()
    elif destino == "exportar_sap":
        from ui.pages import exportar_sap
        exportar_sap.render()
# endregion


# region SESSAO 4 - FLUXO PRINCIPAL
def main() -> None:
    if "user" not in st.session_state:
        tela_login()
        return

    with st.sidebar:
        st.markdown(f"**Usuário:** {st.session_state['user']['name']}")
        escolha = st.radio("Menu", list(MENU.keys()), label_visibility="collapsed")
        if st.button("Sair"):
            st.session_state.clear()
            st.rerun()

    roteador(MENU[escolha])


if __name__ == "__main__":
    main()
# endregion
