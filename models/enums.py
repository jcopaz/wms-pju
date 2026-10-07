# =============================================================================
# VIA WMS - models/enums.py
# Todas as "listas fixas" do sistema (status, tipos) em um so lugar.
# Vantagem: o codigo nao aceita valor invalido e fica facil de entender.
# =============================================================================

from __future__ import annotations

import enum


# region SESSAO 1 - GERAIS
class ActiveStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
# endregion


# region SESSAO 2 - MATERIAIS
class MaterialControlType(str, enum.Enum):
    QUANTITY = "QUANTITY"   # controla so por quantidade
    BATCH = "BATCH"         # controla por lote
    SERIAL = "SERIAL"       # controla por numero de serie
# endregion


# region SESSAO 3 - ESTOQUE
class StockType(str, enum.Enum):
    UNRESTRICTED = "UNRESTRICTED"  # livre uso
    QUALITY = "QUALITY"            # em inspecao
    BLOCKED = "BLOCKED"            # bloqueado
    QUARANTINE = "QUARANTINE"      # quarentena


class OwnershipType(str, enum.Enum):
    MRS = "MRS"                    # material da MRS
    CONTRACTOR = "CONTRACTOR"      # material da contratada
    CONSIGNMENT = "CONSIGNMENT"    # consignado
    OTHER = "OTHER"
# endregion


# region SESSAO 4 - DESTINATARIO / OBJETO DE CUSTO
class RecipientType(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"                    # colaborador proprio
    CONTRACTOR_EMPLOYEE = "CONTRACTOR_EMPLOYEE"  # funcionario de terceiro
    TEAM = "TEAM"                            # equipe
    CONTRACTOR_COMPANY = "CONTRACTOR_COMPANY"    # a propria empresa terceira


class AccountAssignmentType(str, enum.Enum):
    MAINTENANCE_ORDER = "MAINTENANCE_ORDER"  # Ordem de Manutencao -> SAP 261
    COST_CENTER = "COST_CENTER"              # Centro de Custo     -> SAP 201
    WBS_ELEMENT = "WBS_ELEMENT"              # Elemento PEP
    NETWORK = "NETWORK"                      # Rede
    NONE = "NONE"
    OTHER = "OTHER"
# endregion


# region SESSAO 5 - MOVIMENTOS
class MovementDirection(str, enum.Enum):
    INBOUND = "INBOUND"     # entrada
    OUTBOUND = "OUTBOUND"   # saida
    INTERNAL = "INTERNAL"   # transferencia interna


class MovementType(str, enum.Enum):
    ENTRADA_TRANSFERENCIA = "ENTRADA_TRANSFERENCIA"   # recebimento do almox central
    SAIDA_CONSUMO = "SAIDA_CONSUMO"                   # consumo direto
    ENTREGA_CUSTODIA = "ENTREGA_CUSTODIA"             # entrega temporaria
    CONFIRMACAO_CONSUMO = "CONFIRMACAO_CONSUMO"       # confirma o que foi usado
    DEVOLUCAO_CUSTODIA = "DEVOLUCAO_CUSTODIA"         # devolve o que sobrou
    TRANSFERENCIA_LOCAL = "TRANSFERENCIA_LOCAL"       # muda de endereco/deposito
    CONTAGEM_INVENTARIO = "CONTAGEM_INVENTARIO"
    AJUSTE_POSITIVO = "AJUSTE_POSITIVO"
    AJUSTE_NEGATIVO = "AJUSTE_NEGATIVO"
    ESTORNO = "ESTORNO"
# endregion


# region SESSAO 6 - STATUS DE DOCUMENTOS
class DocumentStatus(str, enum.Enum):
    RASCUNHO = "RASCUNHO"
    AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO"
    APROVADO = "APROVADO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    PARCIAL = "PARCIAL"
    CONCLUIDO = "CONCLUIDO"
    AGUARDANDO_SAP = "AGUARDANDO_SAP"
    CONCILIADO = "CONCILIADO"
    DIVERGENTE = "DIVERGENTE"
    CANCELADO = "CANCELADO"
    ESTORNADO = "ESTORNADO"


class CustodyStatus(str, enum.Enum):
    ABERTA = "ABERTA"
    PARCIAL_CONSUMIDA = "PARCIAL_CONSUMIDA"
    PARCIAL_DEVOLVIDA = "PARCIAL_DEVOLVIDA"
    FECHADA_CONSUMO = "FECHADA_CONSUMO"
    FECHADA_DEVOLUCAO = "FECHADA_DEVOLUCAO"
    FECHADA_MISTA = "FECHADA_MISTA"
    DIVERGENTE = "DIVERGENTE"


class InventoryStatus(str, enum.Enum):
    PLANEJADO = "PLANEJADO"
    ABERTO = "ABERTO"
    CONTANDO = "CONTANDO"
    RECONTAGEM = "RECONTAGEM"
    AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO"
    APROVADO = "APROVADO"
    AJUSTADO = "AJUSTADO"
    CANCELADO = "CANCELADO"
# endregion


# region SESSAO 7 - INTEGRACAO SAP
class SAPIntegrationStatus(str, enum.Enum):
    NAO_REQUERIDO = "NAO_REQUERIDO"
    PENDENTE = "PENDENTE"
    EXPORTADO = "EXPORTADO"     # gerou linha no Excel de baixa
    POSTADO = "POSTADO"         # confirmado que baixou no SAP
    FALHA = "FALHA"
    CONCILIADO = "CONCILIADO"
    DIVERGENTE = "DIVERGENTE"
    CANCELADO = "CANCELADO"
# endregion
