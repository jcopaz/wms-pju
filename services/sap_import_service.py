# =============================================================================
# VIA WMS - services/sap_import_service.py
# Le o Excel exportado do SAP e sincroniza o cadastro de materiais + saldo.
# -----------------------------------------------------------------------------
# Julio: o SAP "manda" o Excel; este servico "traduz" cada linha para dentro
# do nosso banco. Ele NAO apaga nada, so atualiza e cria o que falta.
# =============================================================================

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import get_settings
from models.materials import Material, UnitOfMeasure
from models.sap_integration import SAPImportBatch


# region SESSAO 1 - RESULTADO DA IMPORTACAO
@dataclass
class ResultadoImport:
    total: int = 0
    criados: int = 0
    atualizados: int = 0
    erros: int = 0
    mensagens: list[str] = field(default_factory=list)
# endregion


# region SESSAO 2 - LEITURA DO ARQUIVO
def ler_excel(caminho_ou_buffer) -> pd.DataFrame:
    """Le o Excel do SAP como texto (evita perder zeros do MATNR)."""
    df = pd.read_excel(caminho_ou_buffer, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _hash_arquivo(df: pd.DataFrame) -> str:
    conteudo = df.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(conteudo).hexdigest()
# endregion


# region SESSAO 3 - GARANTE UNIDADE DE MEDIDA
def _get_or_create_uom(db: Session, code: str) -> UnitOfMeasure:
    code = (code or "UN").strip().upper()
    uom = db.execute(
        select(UnitOfMeasure).where(UnitOfMeasure.code == code)
    ).scalar_one_or_none()
    if uom is None:
        uom = UnitOfMeasure(code=code, description=code)
        db.add(uom)
        db.flush()
    return uom
# endregion


# region SESSAO 4 - SINCRONIZA MATERIAIS (upsert)
def sincronizar_materiais(
    db: Session, df: pd.DataFrame, usuario_id: Optional[str] = None
) -> ResultadoImport:
    """
    Para cada linha do Excel:
    - Se o MATNR ja existe -> atualiza descricao/grupo/UM.
    - Se nao existe -> cria o material.
    """
    settings = get_settings().sap
    res = ResultadoImport(total=len(df))

    col_mat = settings.col_matnr
    col_desc = settings.col_descricao
    col_um = settings.col_um
    col_grupo = settings.col_grupo

    faltando = [c for c in (col_mat, col_desc) if c not in df.columns]
    if faltando:
        res.erros = res.total
        res.mensagens.append(
            f"Colunas obrigatorias ausentes no Excel: {faltando}. "
            f"Ajuste os nomes em core/config.py (SAPSettings)."
        )
        return res

    for _, row in df.iterrows():
        try:
            matnr = (row.get(col_mat) or "").strip()
            if not matnr:
                res.erros += 1
                continue

            desc = (row.get(col_desc) or "").strip() or matnr
            um = (row.get(col_um) or "UN") if col_um in df.columns else "UN"
            grupo = (row.get(col_grupo) or None) if col_grupo in df.columns else None
            uom = _get_or_create_uom(db, um)

            material = db.execute(
                select(Material).where(Material.sap_material_number == matnr)
            ).scalar_one_or_none()

            if material is None:
                db.add(
                    Material(
                        sap_material_number=matnr,
                        description=desc,
                        material_group=grupo,
                        base_uom_id=uom.id,
                        sap_last_sync_at=datetime.now(timezone.utc),
                    )
                )
                res.criados += 1
            else:
                material.description = desc
                material.material_group = grupo
                material.base_uom_id = uom.id
                material.sap_last_sync_at = datetime.now(timezone.utc)
                res.atualizados += 1
        except Exception as exc:  # captura linha ruim sem parar tudo
            res.erros += 1
            res.mensagens.append(f"Erro na linha: {exc}")

    db.flush()
    return res
# endregion


# region SESSAO 5 - REGISTRA O LOTE DE IMPORTACAO (auditoria)
def registrar_lote(
    db: Session, df: pd.DataFrame, file_name: str, res: ResultadoImport
) -> SAPImportBatch:
    batch = SAPImportBatch(
        file_name=file_name,
        file_hash=_hash_arquivo(df),
        import_type="ESTOQUE",
        total_rows=res.total,
        success_rows=res.criados + res.atualizados,
        error_rows=res.erros,
        status="PROCESSADO" if res.erros == 0 else "PROCESSADO_COM_ERROS",
        log={"mensagens": res.mensagens[:200]},
    )
    db.add(batch)
    db.flush()
    return batch
# endregion


# region SESSAO 6 - FLUXO COMPLETO (le + sincroniza + registra)
def importar_estoque_sap(
    db: Session, caminho_ou_buffer, file_name: str
) -> tuple[ResultadoImport, SAPImportBatch]:
    df = ler_excel(caminho_ou_buffer)
    res = sincronizar_materiais(db, df)
    batch = registrar_lote(db, df, file_name, res)
    return res, batch
# endregion
