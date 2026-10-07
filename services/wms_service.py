# =============================================================================
# VIA WMS - services/wms_service.py
# Regras de negocio do WMS: ENTRADA, SAIDA e TRANSFERENCIA.
# -----------------------------------------------------------------------------
# Julio: este e o "gerente de operacoes". Ele recebe um pedido simples
# (ex.: "entrar 100 pecas") e cuida de tudo: cria o documento, atualiza o
# saldo, define o movimento SAP correspondente e registra a fila de baixa.
# =============================================================================

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from core.config import get_settings
from models.enums import (
    AccountAssignmentType,
    DocumentStatus,
    MovementDirection,
    MovementType,
    OwnershipType,
    SAPIntegrationStatus,
    StockType,
)
from models.movements import StockMovement, StockMovementItem
from models.partners import AccountAssignment
from models.sap_integration import SAPPosting
from services import stock_service


# region SESSAO 1 - OBJETOS DE ENTRADA (o que a tela envia para o servico)
@dataclass
class ItemMovimento:
    material_id: uuid.UUID
    quantidade: Decimal
    uom_id: uuid.UUID
    location_id: uuid.UUID                     # endereco (destino na entrada / origem na saida)
    batch_id: Optional[uuid.UUID] = None
    destination_location_id: Optional[uuid.UUID] = None  # usado na transferencia
    stock_type: StockType = StockType.UNRESTRICTED
    ownership_type: OwnershipType = OwnershipType.MRS
    contractor_ownership_id: Optional[uuid.UUID] = None
    unit_value: Optional[Decimal] = None


@dataclass
class PedidoMovimento:
    warehouse_id: uuid.UUID
    itens: list[ItemMovimento]
    usuario_id: uuid.UUID
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    account_assignment_id: Optional[uuid.UUID] = None
    recipient_id: Optional[uuid.UUID] = None
    contract_id: Optional[uuid.UUID] = None
    operational_order_number: Optional[str] = None
    railway_location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None
    # Na entrada: centros de origem/destino ajudam a decidir 301 vs 311
    mesmo_centro_sap: bool = True
# endregion


# region SESSAO 2 - HELPERS INTERNOS
def _gerar_numero(db: Session, prefixo: str) -> str:
    """Gera um numero legivel tipo ENT-20260814-XXXX."""
    hoje = datetime.now(timezone.utc).strftime("%Y%m%d")
    sufixo = uuid.uuid4().hex[:5].upper()
    return f"{prefixo}-{hoje}-{sufixo}"


def _criar_cabecalho(
    db: Session,
    pedido: PedidoMovimento,
    tipo: MovementType,
    direcao: MovementDirection,
    prefixo: str,
) -> StockMovement:
    mov = StockMovement(
        movement_number=_gerar_numero(db, prefixo),
        movement_type=tipo,
        direction=direcao,
        status=DocumentStatus.EM_ANDAMENTO,
        warehouse_id=pedido.warehouse_id,
        account_assignment_id=pedido.account_assignment_id,
        recipient_id=pedido.recipient_id,
        contract_id=pedido.contract_id,
        operational_order_number=pedido.operational_order_number,
        railway_location=pedido.railway_location,
        latitude=pedido.latitude,
        longitude=pedido.longitude,
        notes=pedido.notes,
        occurred_at=pedido.occurred_at,
        created_by_id=pedido.usuario_id,
    )
    db.add(mov)
    db.flush()
    return mov


def _adicionar_itens(db: Session, mov: StockMovement, itens: list[ItemMovimento]) -> None:
    for i, item in enumerate(itens, start=1):
        total = None
        if item.unit_value is not None:
            total = Decimal(item.unit_value) * Decimal(item.quantidade)
        db.add(
            StockMovementItem(
                movement_id=mov.id,
                line_number=i,
                material_id=item.material_id,
                batch_id=item.batch_id,
                source_location_id=item.location_id,
                destination_location_id=item.destination_location_id,
                quantity=Decimal(item.quantidade),
                uom_id=item.uom_id,
                stock_type=item.stock_type,
                ownership_type=item.ownership_type,
                contractor_ownership_id=item.contractor_ownership_id,
                unit_value=item.unit_value,
                total_value=total,
            )
        )
    db.flush()


def _registrar_posting_sap(
    db: Session, mov: StockMovement, sap_mov_type: str
) -> SAPPosting:
    posting = SAPPosting(
        stock_movement_id=mov.id,
        status=SAPIntegrationStatus.PENDENTE,
        sap_movement_type=sap_mov_type,
        created_by_id=mov.created_by_id,
    )
    db.add(posting)
    db.flush()
    return posting
# endregion


# region SESSAO 3 - ENTRADA (recebimento do Almoxarifado Central)
def registrar_entrada(db: Session, pedido: PedidoMovimento) -> StockMovement:
    """
    Entrada = recebimento de transferencia do deposito principal.
    Movimento SAP: 311 (mesmo centro) ou 301 (entre centros).
    """
    settings = get_settings()
    mov = _criar_cabecalho(
        db, pedido, MovementType.ENTRADA_TRANSFERENCIA,
        MovementDirection.INBOUND, "ENT",
    )
    _adicionar_itens(db, mov, pedido.itens)

    # Credita o saldo de cada item
    for item in pedido.itens:
        stock_service.creditar(
            db,
            warehouse_id=pedido.warehouse_id,
            location_id=item.location_id,
            material_id=item.material_id,
            quantidade=item.quantidade,
            batch_id=item.batch_id,
            stock_type=item.stock_type,
            ownership_type=item.ownership_type,
            contractor_id=item.contractor_ownership_id,
        )

    # Define o movimento SAP de acordo com a origem/destino
    chave = (
        "ENTRADA_TRANSFERENCIA_MESMO_CENTRO"
        if pedido.mesmo_centro_sap
        else "ENTRADA_TRANSFERENCIA_ENTRE_CENTROS"
    )
    sap_mov = settings.rules.movimento_sap[chave]

    mov.status = DocumentStatus.CONCLUIDO
    _registrar_posting_sap(db, mov, sap_mov)
    return mov
# endregion


# region SESSAO 4 - SAIDA (consumo por Ordem ou Centro de Custo)
def registrar_saida(db: Session, pedido: PedidoMovimento) -> StockMovement:
    """
    Saida = consumo de material.
    - Ordem de Manutencao -> SAP 261
    - Centro de Custo      -> SAP 201
    Valida objeto de custo e saldo antes de baixar.
    """
    settings = get_settings()
    rules = settings.rules

    # Regra: toda saida precisa de objeto de custo
    if rules.exigir_objeto_custo_na_saida and pedido.account_assignment_id is None:
        raise ValueError(
            "Saida sem objeto de custo. Informe Ordem de Manutencao "
            "ou Centro de Custo."
        )

    # Descobre o tipo de objeto de custo para escolher o movimento SAP
    tipo_objeto = None
    if pedido.account_assignment_id is not None:
        aa = db.get(AccountAssignment, pedido.account_assignment_id)
        tipo_objeto = aa.assignment_type if aa else None

    if tipo_objeto == AccountAssignmentType.MAINTENANCE_ORDER:
        sap_mov = rules.movimento_sap["SAIDA_ORDEM"]
    elif tipo_objeto == AccountAssignmentType.COST_CENTER:
        sap_mov = rules.movimento_sap["SAIDA_CENTRO_CUSTO"]
    else:
        # PEP, Rede etc.: por seguranca, cai em consumo por objeto generico.
        sap_mov = rules.movimento_sap["SAIDA_ORDEM"]

    mov = _criar_cabecalho(
        db, pedido, MovementType.SAIDA_CONSUMO,
        MovementDirection.OUTBOUND, "SAI",
    )
    _adicionar_itens(db, mov, pedido.itens)

    # Debita o saldo (aqui a trava de concorrencia protege o estoque)
    for item in pedido.itens:
        stock_service.debitar(
            db,
            warehouse_id=pedido.warehouse_id,
            location_id=item.location_id,
            material_id=item.material_id,
            quantidade=item.quantidade,
            batch_id=item.batch_id,
            stock_type=item.stock_type,
            ownership_type=item.ownership_type,
            contractor_id=item.contractor_ownership_id,
            permitir_negativo=not rules.bloquear_saldo_negativo,
        )

    mov.status = DocumentStatus.CONCLUIDO
    _registrar_posting_sap(db, mov, sap_mov)
    return mov
# endregion


# region SESSAO 5 - TRANSFERENCIA (muda de endereco/deposito, sem baixa contabil)
def registrar_transferencia(db: Session, pedido: PedidoMovimento) -> StockMovement:
    """
    Transferencia interna: material muda de endereco fisico.
    Nao gera baixa contabil (nao consome). So reorganiza o saldo local.
    """
    mov = _criar_cabecalho(
        db, pedido, MovementType.TRANSFERENCIA_LOCAL,
        MovementDirection.INTERNAL, "TRF",
    )
    _adicionar_itens(db, mov, pedido.itens)

    for item in pedido.itens:
        if item.destination_location_id is None:
            raise ValueError("Transferencia exige endereco de destino.")

        # Tira da origem
        stock_service.debitar(
            db,
            warehouse_id=pedido.warehouse_id,
            location_id=item.location_id,
            material_id=item.material_id,
            quantidade=item.quantidade,
            batch_id=item.batch_id,
            stock_type=item.stock_type,
            ownership_type=item.ownership_type,
            contractor_id=item.contractor_ownership_id,
        )
        # Coloca no destino
        stock_service.creditar(
            db,
            warehouse_id=pedido.warehouse_id,
            location_id=item.destination_location_id,
            material_id=item.material_id,
            quantidade=item.quantidade,
            batch_id=item.batch_id,
            stock_type=item.stock_type,
            ownership_type=item.ownership_type,
            contractor_id=item.contractor_ownership_id,
        )

    # Transferencia interna nao vai para o SAP como consumo
    mov.status = DocumentStatus.CONCLUIDO
    return mov
# endregion
