# =============================================================================
# VIA WMS - core/config.py
# Configuracoes centrais do sistema (Sentinel-style: tudo por Sessoes)
# -----------------------------------------------------------------------------
# Julio, este arquivo guarda TODAS as configuracoes do sistema em um so lugar.
# Assim voce nunca precisa cacar senha/URL espalhada pelo codigo.
# =============================================================================

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

# Carrega variaveis do arquivo .env (se existir) sem quebrar caso nao exista
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


# region SESSAO 1 - IDENTIDADE VISUAL / MARCA
# -----------------------------------------------------------------------------
APP_NAME = "VIA WMS"
APP_SUBTITLE = "Controle de Materiais - Via Permanente"
APP_VERSION = "0.1.0"

# Paleta oficial (mesma linha do Sentinel: navy + ambar de sinalizacao)
COR_PRIMARIA = "#0B2545"   # Navy - barra, titulos
COR_SECUNDARIA = "#F2A900"  # Ambar sinalizacao - destaques, botoes
COR_SUCESSO = "#1B8A5A"   # Verde - entradas / ok
COR_ALERTA = "#C0392B"    # Vermelho - saidas / divergencias
COR_NEUTRA = "#6B7280"    # Cinza aco - textos secundarios
COR_FUNDO = "#F5F7FA"     # Fundo claro
# endregion


# region SESSAO 2 - BANCO DE DADOS (SUPABASE / POSTGRES)
# -----------------------------------------------------------------------------
# Preencha no arquivo .env. Nunca escreva a senha direto no codigo.
@dataclass
class DatabaseSettings:
    url: str = os.getenv("DATABASE_URL", "")
    schema: str = os.getenv("DB_SCHEMA", "public")
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    @property
    def is_configured(self) -> bool:
        return bool(self.url)
# endregion


# region SESSAO 3 - INTEGRACAO SAP (IMPORT/EXPORT EXCEL)
# -----------------------------------------------------------------------------
@dataclass
class SAPSettings:
    # Nome das colunas esperadas no Excel exportado do SAP (ajustar ao real)
    col_matnr: str = os.getenv("SAP_COL_MATNR", "Material")
    col_descricao: str = os.getenv("SAP_COL_DESC", "Texto breve material")
    col_um: str = os.getenv("SAP_COL_UM", "UMB")
    col_deposito: str = os.getenv("SAP_COL_DEP", "Deposito")
    col_centro: str = os.getenv("SAP_COL_CENTRO", "Centro")
    col_saldo: str = os.getenv("SAP_COL_SALDO", "Estoque")
    col_grupo: str = os.getenv("SAP_COL_GRUPO", "Grupo de mercadorias")

    # Pastas de trabalho para arquivos
    pasta_import: str = os.getenv("SAP_IMPORT_DIR", "data/import")
    pasta_export: str = os.getenv("SAP_EXPORT_DIR", "data/export")
# endregion


# region SESSAO 4 - PARAMETROS DE NEGOCIO DO WMS
# -----------------------------------------------------------------------------
@dataclass
class WMSRules:
    # Bloqueia entrega maior que o saldo disponivel
    bloquear_saldo_negativo: bool = True
    # Exige aprovacao para saidas acima deste valor (R$)
    limite_aprovacao_valor: float = float(os.getenv("WMS_LIMITE_APROVACAO", "5000"))
    # Exige objeto de custo (Ordem ou Centro de Custo) em toda saida
    exigir_objeto_custo_na_saida: bool = True
    # Numero de contagens antes de fechar inventario divergente
    contagens_inventario: int = 2
    # Contagem "cega": nao mostra o saldo do sistema para quem conta
    inventario_contagem_cega: bool = True

    # Mapa movimento WMS -> movimento SAP (usado na exportacao para baixa)
    movimento_sap: dict = field(default_factory=lambda: {
        "ENTRADA_TRANSFERENCIA_MESMO_CENTRO": "311",
        "ENTRADA_TRANSFERENCIA_ENTRE_CENTROS": "301",
        "SAIDA_ORDEM": "261",
        "SAIDA_CENTRO_CUSTO": "201",
        "ESTORNO_ORDEM": "262",
        "ESTORNO_CENTRO_CUSTO": "202",
        "ESTORNO_TRANSFERENCIA": "312",
    })
# endregion


# region SESSAO 5 - AGREGADOR DE CONFIGURACAO
# -----------------------------------------------------------------------------
@dataclass
class Settings:
    db: DatabaseSettings = field(default_factory=DatabaseSettings)
    sap: SAPSettings = field(default_factory=SAPSettings)
    rules: WMSRules = field(default_factory=WMSRules)
    ambiente: str = os.getenv("APP_ENV", "desenvolvimento")


@lru_cache
def get_settings() -> Settings:
    """Retorna a configuracao unica do app (cacheada)."""
    return Settings()
# endregion
