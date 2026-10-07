# =============================================================================
# VIA WMS - scripts/seed.py
# Cria as tabelas e carrega dados minimos para voce testar o sistema.
# Rodar:  python scripts/seed.py
# =============================================================================

from __future__ import annotations

import sys
from pathlib import Path

# Garante que o Python enxergue a raiz do projeto
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.database import criar_tabelas, get_session  # noqa: E402
from models.enums import AccountAssignmentType, RecipientType  # noqa: E402
from models.materials import Material, UnitOfMeasure  # noqa: E402
from models.organization import (  # noqa: E402
    OrganizationUnit,
    SAPPlant,
    SAPStorageLocation,
    StorageLocation,
    Warehouse,
)
from models.partners import AccountAssignment, Recipient  # noqa: E402


def run() -> None:
    print("Criando tabelas...")
    criar_tabelas()

    with get_session() as db:
        print("Inserindo dados de exemplo...")

        # Unidade organizacional (coordenacao)
        gg = OrganizationUnit(code="GG-INFRA-SP", name="GG Infraestrutura SP")
        db.add(gg)
        db.flush()

        # Centro e deposito SAP
        centro = SAPPlant(code="1000", name="Centro MRS Exemplo")
        db.add(centro)
        db.flush()
        dep_sap = SAPStorageLocation(plant_id=centro.id, code="0001", name="Dep. Local VP")
        db.add(dep_sap)
        db.flush()

        # Deposito local + endereco
        wh = Warehouse(
            code="VP-JUNDIAI", name="Estoque VP Jundiaí",
            organization_unit_id=gg.id, sap_storage_location_id=dep_sap.id,
        )
        db.add(wh)
        db.flush()
        end = StorageLocation(warehouse_id=wh.id, code="A-01", name="Prateleira A-01")
        db.add(end)

        # Unidade de medida + material
        un = UnitOfMeasure(code="UN", description="Unidade")
        db.add(un)
        db.flush()
        db.add(Material(sap_material_number="000000000010001",
                        description="Grampo elástico", base_uom_id=un.id))

        # Objetos de custo
        db.add(AccountAssignment(assignment_type=AccountAssignmentType.MAINTENANCE_ORDER,
                                 sap_code="OM-1001", description="Ordem exemplo"))
        db.add(AccountAssignment(assignment_type=AccountAssignmentType.COST_CENTER,
                                 sap_code="CC-2002", description="Centro custo exemplo"))

        # Recebedor
        db.add(Recipient(recipient_type=RecipientType.EMPLOYEE, name="Equipe VP 01"))

    print("Pronto! Rode:  streamlit run app.py")


if __name__ == "__main__":
    run()
