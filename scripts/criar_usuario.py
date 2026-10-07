# =============================================================================
# VIA WMS - scripts/criar_usuario.py
# Cria um usuario (ou troca a senha de um existente) para o login provisorio.
# Rodar:   python scripts/criar_usuario.py
#          python scripts/criar_usuario.py --desativar MATRICULA
# A senha e pedida sem aparecer na tela.
# =============================================================================

from __future__ import annotations

import argparse
import getpass
import logging
import sys
from pathlib import Path

# Garante que o Python enxergue a raiz do projeto
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.database import get_session  # noqa: E402
from services import auth_service  # noqa: E402


def main() -> int:
    """Le os dados no terminal e grava o usuario.

    Returns:
        Codigo de saida (0 = ok).
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Cadastro de usuarios do VIA WMS")
    parser.add_argument("--desativar", metavar="LOGIN", help="bloqueia o acesso do login")
    args = parser.parse_args()

    if args.desativar:
        with get_session() as db:
            ok = auth_service.desativar_usuario(db, args.desativar)
        print("Usuario desativado." if ok else "Usuario nao encontrado.")
        return 0 if ok else 1

    login = input("Login (matricula): ").strip()
    nome = input("Nome: ").strip()
    email = input("E-mail (opcional): ").strip() or None
    senha = getpass.getpass(f"Senha (min. {auth_service.SENHA_MINIMA} caracteres): ")
    if senha != getpass.getpass("Repita a senha: "):
        print("As senhas nao conferem.")
        return 1

    try:
        with get_session() as db:
            auth_service.salvar_usuario(db, login, nome, senha, email)
    except ValueError as erro:
        print(f"Erro: {erro}")
        return 1
    print(f"Pronto! '{login}' ja pode entrar no sistema.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
