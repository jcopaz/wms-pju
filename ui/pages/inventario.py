# =============================================================================
# VIA WMS - ui/pages/inventario.py
# Tela de INVENTARIO: abre campanha, registra contagem (cega) e ve diferencas.
# =============================================================================

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import streamlit as st
from sqlalchemy import select

from core.config import get_settings
from core.database import get_session
from models.inventory import InventoryCount, InventorySession
from models.materials import Material
from models.organization import StorageLocation, Warehouse
from models.enums import InventoryStatus
from ui.theme import cabecalho


def render() -> None:
    cabecalho("Inventário")
    cega = get_settings().rules.inventario_contagem_cega
    st.caption(
        "Contagem física do estoque. "
        + ("Contagem cega ativada: o saldo do sistema fica oculto." if cega
           else "Contagem aberta.")
    )

    with get_session() as db:
        depositos = list(db.execute(select(Warehouse)).scalars().all())
        if not depositos:
            st.warning("Cadastre um depósito antes.")
            return
        dep = st.selectbox(
            "Depósito", depositos, format_func=lambda w: f"{w.code} - {w.name}"
        )

        tab_abrir, tab_contar = st.tabs(["📋 Abrir campanha", "🔢 Registrar contagem"])

        # region ABRIR CAMPANHA
        with tab_abrir:
            if st.button("Abrir nova campanha de inventário"):
                sess = InventorySession(
                    inventory_number=f"INV-{datetime.now(timezone.utc):%Y%m%d}-"
                                     f"{uuid.uuid4().hex[:4].upper()}",
                    warehouse_id=dep.id,
                    status=InventoryStatus.ABERTO,
                    cutoff_at=datetime.now(timezone.utc),
                    blind_count=cega,
                )
                db.add(sess)
                db.flush()
                st.success(f"Campanha aberta: {sess.inventory_number}")
        # endregion

        # region REGISTRAR CONTAGEM
        with tab_contar:
            sessoes = db.execute(
                select(InventorySession).where(
                    InventorySession.warehouse_id == dep.id,
                    InventorySession.status.in_(
                        [InventoryStatus.ABERTO, InventoryStatus.CONTANDO,
                         InventoryStatus.RECONTAGEM]
                    ),
                )
            ).scalars().all()

            if not sessoes:
                st.info("Nenhuma campanha aberta. Abra uma na aba anterior.")
                return

            sess = st.selectbox(
                "Campanha", sessoes, format_func=lambda s: s.inventory_number
            )
            materiais = list(db.execute(select(Material)).scalars().all())
            enderecos = db.execute(
                select(StorageLocation).where(StorageLocation.warehouse_id == dep.id)
            ).scalars().all()

            if not materiais or not enderecos:
                st.warning("Cadastre materiais e endereços antes.")
                return

            material = st.selectbox(
                "Material", materiais,
                format_func=lambda m: f"{m.sap_material_number} - {m.description}",
            )
            endereco = st.selectbox("Endereço", enderecos, format_func=lambda e: e.name)
            contado = st.number_input("Quantidade contada", min_value=0.0, step=1.0)

            if st.button("Salvar contagem"):
                # Em contagem cega, o sistema NAO mostra o saldo, mas registra
                # o valor de sistema por tras para calcular a diferenca depois.
                sistema = Decimal("0")  # substituir por saldo real do StockBalance
                cont = InventoryCount(
                    inventory_session_id=sess.id,
                    location_id=endereco.id,
                    material_id=material.id,
                    count_number=1,
                    system_quantity=sistema,
                    counted_quantity=Decimal(str(contado)),
                    difference_quantity=Decimal(str(contado)) - sistema,
                    counted_by_id=st.session_state["user"]["id"],
                    counted_at=datetime.now(timezone.utc),
                )
                db.add(cont)
                sess.status = InventoryStatus.CONTANDO
                db.flush()
                st.success("Contagem registrada.")
        # endregion
