# KB_02 — Modelo de Dados (ORM)

**Versão:** v0.1.0 · **Atualizado em:** 2026-08-14

---

## 1. Convenções

- Chave primária: **UUID** (`UUIDPrimaryKeyMixin`).
- Datas automáticas: `created_at` / `updated_at` (`TimestampMixin`).
- Auditoria de autoria: `created_by_id` / `updated_by_id` (`AuditUserMixin`).
- Padrão SQLAlchemy 2 declarativo com `Mapped` / `mapped_column`.

## 2. Domínios e tabelas

### Organização (`models/organization.py`)
- `OrganizationUnit` — coordenações / GG (hierárquico).
- `User`, `Role`, `UserRole` — usuários e perfis por depósito.
- `SAPPlant` (Centro) e `SAPStorageLocation` (Depósito SAP).
- `Warehouse` — depósito local do WMS, ligado ao depósito SAP.
- `StorageLocation` — endereço físico (prateleira/rua/posição), hierárquico.

### Materiais (`models/materials.py`)
- `UnitOfMeasure` — unidade de medida.
- `Material` — **`sap_material_number` (MATNR)** é a chave de sincronização.
- `MaterialBatch` — lote. `MaterialSerial` — número de série.

### Parceiros e custo (`models/partners.py`)
- `Contractor` — contratada (CNPJ). `Contract` — contrato.
- `Recipient` — quem recebe (próprio, terceiro, equipe, empresa).
- `AccountAssignment` — objeto de custo SAP (Ordem, Centro de Custo, PEP, Rede).

### Estoque (`models/stock.py`)
- `StockBalance` — saldo por depósito/endereço/material/lote/tipo/propriedade.
  - `quantity`, `reserved_quantity`, `version` (concorrência).
  - `available_quantity` = quantity − reserved.
  - Constraints: quantidade e reservado ≥ 0.

### Movimentos (`models/movements.py`)
- `StockMovement` — cabeçalho (tipo, direção, status, depósito, objeto de
  custo, recebedor, contrato, geolocalização, occurred_at).
- `StockMovementItem` — itens (material, lote, origem, destino, quantidade,
  propriedade, valor). Constraint: quantidade > 0.

### Custódia (`models/custody.py`)
- `MaterialCustody` — entrega temporária a um recebedor.
- `MaterialCustodyItem` — entregue x consumido x devolvido x perdido.
  - `open_quantity` = saldo ainda em poder do recebedor.
  - Constraint: soma de resolvido ≤ entregue.

### Inventário (`models/inventory.py`)
- `InventorySession` — campanha (cutoff, contagem cega, status).
- `InventoryCount` — contagem/recontagem por endereço/material.

### Integração SAP (`models/sap_integration.py`)
- `SAPImportBatch` — cada Excel do SAP importado (auditoria).
- `SAPPosting` — fila de baixa (movimento SAP, documento de material, status).
- `Attachment` — evidências (foto, nota). `AuditLog` — trilha de auditoria.

## 3. Relacionamentos-chave

- `Warehouse` → `SAPStorageLocation` (base da conciliação com o SAP).
- `StockMovement` 1—N `StockMovementItem`.
- `MaterialCustody` 1—N `MaterialCustodyItem` (liga-se ao movimento de saída).
- `SAPPosting` N—1 `StockMovement` (uma baixa por movimento).

## 4. Regras de integridade (banco)

- Saldo não negativo (CheckConstraint).
- Unicidade de MATNR em `Material`.
- Unicidade de número de documento em `StockMovement`.
- Índices de busca em `StockBalance` (lookup) e `AuditLog`.

## 5. Pendências deste domínio

- Adicionar tabela de **reserva** formal (hoje só há `reserved_quantity`).
- DTOs Pydantic para cada agregado (a criar conforme Regra Absoluta).
- Migrações Alembic (substituir `criar_tabelas()` no futuro).
