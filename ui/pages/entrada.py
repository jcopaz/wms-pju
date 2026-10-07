# =============================================================================
# VIA WMS - ui/pages/entrada.py
# Tela de ENTRADA de material (recebimento). Pensada para o celular.
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


def _listar(db, model):
    return list(db.execute(select(model)).scalars().all())


def render() -> None:
    cabecalho("Entrada de material")
    st.caption("Recebimento do Almoxarifado Central para o estoque local.")

    with get_session() as db:
        depositos = _listar(db, Warehouse)
        materiais = _listar(db, Material)

        if not depositos or not materiais:
            st.warning("Cadastre depósitos e importe materiais do SAP antes.")
            return

        dep = st.selectbox(
            "Depósito", depositos, format_func=lambda w: f"{w.code} - {w.name}"
        )
        enderecos = db.execute(
            select(StorageLocation).where(StorageLocation.warehouse_id == dep.id)
        ).scalars().all()

        material = st.selectbox(
            "Material",
            materiais,
            format_func=lambda m: f"{m.sap_material_number} - {m.description}",
        )
        endereco = st.selectbox(
            "Endereço de guarda",
            enderecos,
            format_func=lambda e: e.name,
        ) if enderecos else None

        qtd = st.number_input("Quantidade", min_value=0.0, step=1.0)
        mesmo_centro = st.toggle("Mesmo centro SAP (311)", value=True,
                                 help="Desligue se a origem for outro centro (301).")

        # Captura de foto (evidencia) e localizacao pelo celular
        foto = st.camera_input("Foto da nota/evidência (opcional)")
        st.caption("Movimento SAP: 311 (mesmo centro) ou 301 (entre centros).")

        if st.button("✅ Confirmar entrada"):
            if not endereco:
                st.error("Cadastre um endereço de guarda para este depósito.")
                return
            if qtd <= 0:
                st.error("Informe uma quantidade maior que zero.")
                return

            pedido = PedidoMovimento(
                warehouse_id=dep.id,
                usuario_id=uuid.uuid4(),  # trocar pelo usuario logado real
                mesmo_centro_sap=mesmo_centro,
                itens=[
                    ItemMovimento(
                        material_id=material.id,
                        quantidade=Decimal(str(qtd)),
                        uom_id=material.base_uom_id,
                        location_id=endereco.id,
                    )
                ],
            )
            mov = wms_service.registrar_entrada(db, pedido)
            st.success(f"Entrada registrada: {mov.movement_number}")
            st.balloons()
