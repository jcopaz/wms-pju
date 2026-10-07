# =============================================================================
# VIA WMS - services/sap_export_service.py
# Gera o Excel PADRONIZADO para baixa no SAP, a partir das saidas pendentes.
# -----------------------------------------------------------------------------
# Julio: as saidas registradas no celular ficam "aguardando baixa". Este
# servico junta todas, monta um Excel no layout que o SAP/MIGO espera e marca
# como EXPORTADO. Depois que alguem confirma a baixa, marcamos como POSTADO.
# =============================================================================

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.enums import SAPIntegrationStatus
from models.materials import Material
from models.movements import StockMovement, StockMovementItem
from models.partners import AccountAssignment
from models.sap_integration import SAPPosting


# region SESSAO 1 - MONTA AS LINHAS DE BAIXA
def _linhas_para_baixa(db: Session, postings: list[SAPPosting]) -> list[dict]:
    linhas: list[dict] = []
    for posting in postings:
        mov = db.get(StockMovement, posting.stock_movement_id)
        if mov is None:
            continue

        objeto_custo = ""
        if mov.account_assignment_id:
            aa = db.get(AccountAssignment, mov.account_assignment_id)
            objeto_custo = aa.sap_code if aa else ""

        itens = db.execute(
            select(StockMovementItem).where(
                StockMovementItem.movement_id == mov.id
            )
        ).scalars().all()

        for item in itens:
            material = db.get(Material, item.material_id)
            linhas.append(
                {
                    "Documento_WMS": mov.movement_number,
                    "Data": mov.occurred_at.strftime("%d.%m.%Y"),
                    "Tipo_Movimento_SAP": posting.sap_movement_type,
                    "Material_SAP": material.sap_material_number if material else "",
                    "Descricao": material.description if material else "",
                    "Quantidade": float(item.quantity),
                    "Objeto_Custo": objeto_custo,
                    "Ordem_Servico": mov.operational_order_number or "",
                    "Local_Via": mov.railway_location or "",
                    "ID_Posting": str(posting.id),
                }
            )
    return linhas
# endregion


# region SESSAO 2 - GERA O EXCEL EM MEMORIA
def gerar_excel_baixa(
    db: Session, limite: Optional[int] = None
) -> tuple[bytes, str, list[SAPPosting]]:
    """
    Retorna: (bytes do Excel, nome do arquivo, lista de postings incluidos).
    Pega tudo que esta PENDENTE de baixa.
    """
    stmt = select(SAPPosting).where(
        SAPPosting.status == SAPIntegrationStatus.PENDENTE
    )
    if limite:
        stmt = stmt.limit(limite)

    postings = list(db.execute(stmt).scalars().all())
    linhas = _linhas_para_baixa(db, postings)

    df = pd.DataFrame(linhas)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Baixa_SAP")
    buffer.seek(0)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_name = f"VIA_WMS_baixa_SAP_{stamp}.xlsx"
    return buffer.getvalue(), file_name, postings
# endregion


# region SESSAO 3 - MARCA COMO EXPORTADO
def marcar_exportado(db: Session, postings: list[SAPPosting]) -> str:
    """Depois de gerar o Excel, marca os postings como EXPORTADO."""
    lote = uuid.uuid4().hex[:10].upper()
    agora = datetime.now(timezone.utc)
    for p in postings:
        p.status = SAPIntegrationStatus.EXPORTADO
        p.export_batch_id = lote
        p.exported_at = agora
    db.flush()
    return lote
# endregion


# region SESSAO 4 - CONFIRMA BAIXA (importa retorno do SAP)
def confirmar_baixa(
    db: Session,
    posting_id: uuid.UUID,
    documento_material: str,
    ano_fiscal: str,
) -> SAPPosting:
    """
    Quando o SAP devolve o numero do documento de material, registramos aqui.
    Assim o movimento passa de EXPORTADO para POSTADO (baixa confirmada).
    """
    posting = db.get(SAPPosting, posting_id)
    if posting is None:
        raise ValueError("Posting nao encontrado.")
    posting.sap_material_document = documento_material
    posting.sap_fiscal_year = ano_fiscal
    posting.status = SAPIntegrationStatus.POSTADO
    posting.posted_at = datetime.now(timezone.utc)
    db.flush()
    return posting
# endregion
