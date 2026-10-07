# =============================================================================
# VIA WMS - ui/pages/saida.py
# Tela de SAIDA (consumo) por Ordem de Manutencao ou Centro de Custo.
# =============================================================================

from __future__ import annotations

from decimal import Decimal

import streamlit as st
from sqlalchemy import select

from core.database import get_session
from models.materials import Material
from models.organization import StorageLocation, Warehouse
from models.partners import AccountAssignment, Recipient
from services import stock_service, wms_service
from services.wms_service import ItemMovimento, PedidoMovimento
from ui.theme import cabecalho


def _listar(db, model):
    return list(db.execute(select(model)).scalars().all())


def render() -> None:
    cabecalho("Saída de material")
    st.caption("Consumo vinculado a Ordem (261) ou Centro de Custo (201).")

    with get_session() as db:
        depositos = _listar(db, Warehouse)
        materiais = _listar(db, Material)
        objetos = _listar(db, AccountAssignment)
        recebedores = _listar(db, Recipient)

        if not depositos or not materiais:
            st.warning("Cadastre depósitos e importe materiais antes.")
            return

        dep = st.selectbox(
            "Depósito", depositos, format_func=lambda w: f"{w.code} - {w.name}"
        )
        material = st.selectbox(
            "Material",
            materiais,
            format_func=lambda m: f"{m.sap_material_number} - {m.description}",
        )

        # Mostra o saldo disponivel do material escolhido
        disp = stock_service.saldo_disponivel(
            db, warehouse_id=dep.id, material_id=material.id
        )
        st.metric("Saldo disponível", f"{disp:.0f}")

        enderecos = db.execute(
            select(StorageLocation).where(StorageLocation.warehouse_id == dep.id)
        ).scalars().all()
        endereco = st.selectbox(
            "Endereço de origem", enderecos, format_func=lambda e: e.name
        ) if enderecos else None

        objeto = st.selectbox(
            "Objeto de custo (Ordem/Centro de Custo)",
            objetos,
            format_func=lambda a: f"{a.assignment_type.value} - {a.sap_code}",
        ) if objetos else None

        recebedor = st.selectbox(
            "Recebedor (opcional)",
            [None] + recebedores,
            format_func=lambda r: "—" if r is None else f"{r.recipient_type.value} - {r.name}",
        )

        qtd = st.number_input("Quantidade", min_value=0.0, step=1.0)
        os_num = st.text_input("Ordem de Serviço / OM (texto livre, opcional)")
        via = st.text_input("Local na via (km/trecho, opcional)")
        st.camera_input("Foto da entrega (opcional)")

        if st.button("⬆️ Confirmar saída"):
            if not objeto:
                st.error("Selecione um objeto de custo (Ordem ou Centro de Custo).")
                return
            if not endereco:
                st.error("Selecione o endereço de origem.")
                return
            if qtd <= 0:
                st.error("Informe uma quantidade válida.")
                return

            pedido = PedidoMovimento(
                warehouse_id=dep.id,
                usuario_id=st.session_state["user"]["id"],
                account_assignment_id=objeto.id,
                recipient_id=recebedor.id if recebedor else None,
                operational_order_number=os_num or None,
                railway_location=via or None,
                itens=[
                    ItemMovimento(
                        material_id=material.id,
                        quantidade=Decimal(str(qtd)),
                        uom_id=material.base_uom_id,
                        location_id=endereco.id,
                    )
                ],
            )
            try:
                mov = wms_service.registrar_saida(db, pedido)
                st.success(f"Saída registrada: {mov.movement_number}")
            except Exception as exc:
                st.error(f"Não foi possível registrar a saída: {exc}")
