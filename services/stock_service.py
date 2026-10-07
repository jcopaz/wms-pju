# =============================================================================
# VIA WMS - services/stock_service.py
# Motor de saldo: soma/subtrai estoque com trava de concorrencia.
# Nenhum outro servico deve mexer no saldo direto - sempre passa por aqui.
# =============================================================================

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import OwnershipType, StockType
from models.stock import StockBalance


# region SESSAO 1 - EXCECOES DE NEGOCIO
class SaldoInsuficienteError(Exception):
    """Disparada quando tenta tirar mais do que existe no endereco."""
# endregion


# region SESSAO 2 - BUSCA/CRIA A LINHA DE SALDO
def _get_or_create_balance(
    db: Session,
    warehouse_id: uuid.UUID,
    location_id: uuid.UUID,
    material_id: uuid.UUID,
    batch_id: Optional[uuid.UUID],
    stock_type: StockType,
    ownership_type: OwnershipType,
    contractor_id: Optional[uuid.UUID],
    lock: bool = True,
) -> StockBalance:
    stmt = select(StockBalance).where(
        StockBalance.warehouse_id == warehouse_id,
        StockBalance.location_id == location_id,
        StockBalance.material_id == material_id,
        StockBalance.batch_id == batch_id,
        StockBalance.stock_type == stock_type,
        StockBalance.ownership_type == ownership_type,
        StockBalance.contractor_id == contractor_id,
    )
    if lock:
        # SELECT ... FOR UPDATE: trava a linha ate o commit,
        # impedindo duas baixas simultaneas de "furar" o saldo.
        stmt = stmt.with_for_update()

    balance = db.execute(stmt).scalar_one_or_none()
    if balance is None:
        balance = StockBalance(
            warehouse_id=warehouse_id,
            location_id=location_id,
            material_id=material_id,
            batch_id=batch_id,
            stock_type=stock_type,
            ownership_type=ownership_type,
            contractor_id=contractor_id,
            quantity=Decimal("0"),
            reserved_quantity=Decimal("0"),
        )
        db.add(balance)
        db.flush()
    return balance
# endregion


# region SESSAO 3 - ENTRADA (soma saldo)
def creditar(
    db: Session,
    *,
    warehouse_id: uuid.UUID,
    location_id: uuid.UUID,
    material_id: uuid.UUID,
    quantidade: Decimal,
    batch_id: Optional[uuid.UUID] = None,
    stock_type: StockType = StockType.UNRESTRICTED,
    ownership_type: OwnershipType = OwnershipType.MRS,
    contractor_id: Optional[uuid.UUID] = None,
) -> StockBalance:
    balance = _get_or_create_balance(
        db, warehouse_id, location_id, material_id, batch_id,
        stock_type, ownership_type, contractor_id, lock=True,
    )
    balance.quantity = Decimal(balance.quantity) + Decimal(quantidade)
    balance.version += 1
    return balance
# endregion


# region SESSAO 4 - SAIDA (subtrai saldo, valida disponibilidade)
def debitar(
    db: Session,
    *,
    warehouse_id: uuid.UUID,
    location_id: uuid.UUID,
    material_id: uuid.UUID,
    quantidade: Decimal,
    batch_id: Optional[uuid.UUID] = None,
    stock_type: StockType = StockType.UNRESTRICTED,
    ownership_type: OwnershipType = OwnershipType.MRS,
    contractor_id: Optional[uuid.UUID] = None,
    permitir_negativo: bool = False,
) -> StockBalance:
    balance = _get_or_create_balance(
        db, warehouse_id, location_id, material_id, batch_id,
        stock_type, ownership_type, contractor_id, lock=True,
    )
    disponivel = balance.available_quantity
    if not permitir_negativo and Decimal(quantidade) > disponivel:
        raise SaldoInsuficienteError(
            f"Saldo insuficiente. Disponivel: {disponivel}, "
            f"solicitado: {quantidade}."
        )
    balance.quantity = Decimal(balance.quantity) - Decimal(quantidade)
    balance.version += 1
    return balance
# endregion


# region SESSAO 5 - CONSULTA DE SALDO DISPONIVEL
def saldo_disponivel(
    db: Session,
    *,
    warehouse_id: uuid.UUID,
    material_id: uuid.UUID,
    location_id: Optional[uuid.UUID] = None,
) -> Decimal:
    stmt = select(StockBalance).where(
        StockBalance.warehouse_id == warehouse_id,
        StockBalance.material_id == material_id,
    )
    if location_id is not None:
        stmt = stmt.where(StockBalance.location_id == location_id)

    total = Decimal("0")
    for b in db.execute(stmt).scalars():
        total += b.available_quantity
    return total
# endregion
