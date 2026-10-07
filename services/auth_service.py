# =============================================================================
# VIA WMS - services/auth_service.py
# Login provisorio: usuarios na tabela `users` com senha em hash PBKDF2.
# -----------------------------------------------------------------------------
# Julio: este e o "porteiro" do sistema enquanto o AD/Entra ID nao chega.
# A senha nunca e gravada pura: guardamos so o hash (com sal aleatorio).
# Para criar/trocar senha de alguem:  python scripts/criar_usuario.py
# =============================================================================

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import secrets
import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.organization import User

logger = logging.getLogger(__name__)


# region SESSAO 1 - PARAMETROS DO HASH
# -----------------------------------------------------------------------------
ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000          # recomendacao OWASP para PBKDF2-SHA256
TAMANHO_SAL = 16
SENHA_MINIMA = 8
# endregion


# region SESSAO 2 - OBJETO DE SAIDA (usuario autenticado)
@dataclass(frozen=True)
class UsuarioLogado:
    """Dados do usuario autenticado guardados na sessao do Streamlit.

    Attributes:
        id: chave do usuario na tabela `users` (vai para created_by_id).
        login: matricula/login digitado.
        name: nome para exibicao.
    """

    id: uuid.UUID
    login: str
    name: str
# endregion


# region SESSAO 3 - HASH E VERIFICACAO DE SENHA
# -----------------------------------------------------------------------------
def gerar_hash(senha: str) -> str:
    """Gera o hash PBKDF2 da senha, no formato algoritmo$iteracoes$sal$hash.

    Args:
        senha: senha em texto puro.
    Returns:
        Texto pronto para gravar em `users.password_hash`.
    """
    sal = secrets.token_bytes(TAMANHO_SAL)
    chave = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, ITERACOES)
    return "$".join([
        ALGORITMO,
        str(ITERACOES),
        base64.b64encode(sal).decode("ascii"),
        base64.b64encode(chave).decode("ascii"),
    ])


def verificar_senha(senha: str, hash_gravado: Optional[str]) -> bool:
    """Confere a senha digitada contra o hash gravado (comparacao em tempo constante).

    Args:
        senha: senha digitada no login.
        hash_gravado: valor de `users.password_hash` (pode ser vazio).
    Returns:
        True se a senha confere.
    """
    if not hash_gravado:
        return False
    try:
        algoritmo, iteracoes, sal_b64, chave_b64 = hash_gravado.split("$")
    except ValueError:
        logger.warning("Hash de senha em formato invalido.")
        return False
    if algoritmo != ALGORITMO:
        logger.warning("Algoritmo de hash desconhecido: %s", algoritmo)
        return False
    chave = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), base64.b64decode(sal_b64), int(iteracoes)
    )
    return hmac.compare_digest(chave, base64.b64decode(chave_b64))
# endregion


# region SESSAO 4 - LOGIN
# -----------------------------------------------------------------------------
def autenticar(db: Session, login: str, senha: str) -> Optional[UsuarioLogado]:
    """Valida login e senha de um usuario ativo.

    Args:
        db: sessao do banco.
        login: matricula/login (sem diferenciar maiusculas).
        senha: senha digitada.
    Returns:
        UsuarioLogado se as credenciais conferem; None caso contrario.
    """
    login_limpo = login.strip().lower()
    usuario = db.scalar(select(User).where(func.lower(User.login) == login_limpo))
    if usuario is None or not usuario.active:
        # Mesmo custo de CPU quando o usuario nao existe (nao revela quem existe)
        verificar_senha(senha, gerar_hash("senha-inexistente"))
        logger.warning("Login recusado (usuario inexistente ou inativo): %s", login_limpo)
        return None
    if not verificar_senha(senha, usuario.password_hash):
        logger.warning("Login recusado (senha incorreta): %s", login_limpo)
        return None
    logger.info("Login ok: %s", usuario.login)
    return UsuarioLogado(id=usuario.id, login=usuario.login, name=usuario.name)
# endregion


# region SESSAO 5 - CADASTRO / TROCA DE SENHA
# -----------------------------------------------------------------------------
def salvar_usuario(
    db: Session,
    login: str,
    nome: str,
    senha: str,
    email: Optional[str] = None,
) -> User:
    """Cria o usuario ou, se o login ja existe, atualiza nome, e-mail e senha.

    Args:
        db: sessao do banco.
        login: matricula/login (gravado em minusculas).
        nome: nome para exibicao.
        senha: nova senha (minimo SENHA_MINIMA caracteres).
        email: e-mail opcional.
    Returns:
        O registro `User` gravado.
    Raises:
        ValueError: se login, nome ou senha forem invalidos.
    """
    login_limpo = login.strip().lower()
    if not login_limpo or not nome.strip():
        raise ValueError("Login e nome sao obrigatorios.")
    if len(senha) < SENHA_MINIMA:
        raise ValueError(f"A senha precisa ter pelo menos {SENHA_MINIMA} caracteres.")

    usuario = db.scalar(select(User).where(func.lower(User.login) == login_limpo))
    if usuario is None:
        usuario = User(login=login_limpo, name=nome.strip(), registration_number=login_limpo)
        db.add(usuario)
        logger.info("Usuario criado: %s", login_limpo)
    else:
        usuario.name = nome.strip()
        usuario.active = True
        logger.info("Usuario atualizado (senha trocada): %s", login_limpo)
    usuario.email = email or usuario.email
    usuario.password_hash = gerar_hash(senha)
    db.flush()
    return usuario


def desativar_usuario(db: Session, login: str) -> bool:
    """Bloqueia o acesso de um usuario sem apagar o historico dele.

    Args:
        db: sessao do banco.
        login: matricula/login.
    Returns:
        True se o usuario existia e foi desativado.
    """
    usuario = db.scalar(select(User).where(func.lower(User.login) == login.strip().lower()))
    if usuario is None:
        logger.warning("Desativar: usuario nao encontrado: %s", login)
        return False
    usuario.active = False
    logger.info("Usuario desativado: %s", usuario.login)
    return True
# endregion
