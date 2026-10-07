# =============================================================================
# VIA WMS - ui/pages/transferencia.py
# Tela de TRANSFERENCIA interna (muda de endereco). Sem baixa contabil.
# =============================================================================

from __future__ import annotations

import uuid
from decimal import Decimal

import streamlit as st
from sqlalchemy import select

from core.database import get_session
from models.materials import Material
from models.organization import StorageLocation, Warehouse
from services import wms_service
from services.wms_service import ItemMovimento, PedidoMovimento
from ui.theme import cabecalho


def render() -> None:
    cabecalho("Transferência interna")
    st.caption("Move material entre endereços do mesmo depósito. Não consome estoque.")

    with get_session() as db:
        depositos = list(db.execute(select(Warehouse)).scalars().all())
        materiais = list(db.execute(select(Material)).scalars().all())
        if not depositos or not materiais:
            st.warning("Cadastre depósitos e materiais antes.")
            return

        dep = st.selectbox(
            "Depósito", depositos, format_func=lambda w: f"{w.code} - {w.name}"
        )
        enderecos = db.execute(
            select(StorageLocation).where(StorageLocation.warehouse_id == dep.id)
        ).scalars().all()
        if len(enderecos) < 2:
            st.warning("Cadastre pelo menos 2 endereços neste depósito.")
            return

        material = st.selectbox(
            "Material", materiais,
            format_func=lambda m: f"{m.sap_material_number} - {m.description}",
        )
        origem = st.selectbox("Origem", enderecos, format_func=lambda e: e.name)
        destino = st.selectbox("Destino", enderecos, format_func=lambda e: e.name)
        qtd = st.number_input("Quantidade", min_value=0.0, step=1.0)

        if st.button("🔁 Confirmar transferência"):
            if origem.id == destino.id:
                st.error("Origem e destino devem ser diferentes.")
                return
            if qtd <= 0:
                st.error("Informe uma quantidade válida.")
                return
            pedido = PedidoMovimento(
                warehouse_id=dep.id,
                usuario_id=uuid.uuid4(),
                itens=[
                    ItemMovimento(
                        material_id=material.id,
                        quantidade=Decimal(str(qtd)),
                        uom_id=material.base_uom_id,
                        location_id=origem.id,
                        destination_location_id=destino.id,
                    )
                ],
            )
            try:
                mov = wms_service.registrar_transferencia(db, pedido)
                st.success(f"Transferência registrada: {mov.movement_number}")
            except Exception as exc:
                st.error(f"Erro: {exc}")
