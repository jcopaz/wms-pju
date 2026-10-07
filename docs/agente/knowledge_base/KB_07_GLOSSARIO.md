# KB_07 — Glossário

**Versão:** v0.1.0 · **Atualizado em:** 2026-08-14

---

## Termos de negócio (Via Permanente / MRS)

| Termo | Significado |
|---|---|
| Via Permanente (VP) | Estrutura da ferrovia: trilhos, dormentes, fixações, lastro. |
| Almoxarifado Central | Estoque principal que abastece as coordenações. |
| Estoque local/intermediário | Estoque da coordenação, controlado pelo WMS. |
| Custódia | Material entregue temporariamente, ainda não consumido. |
| Objeto de custo | Onde o consumo é lançado (Ordem, Centro de Custo, PEP). |
| Prestador/Terceiro | Empresa contratada (identificada por CNPJ + contrato). |

## Termos SAP

| Termo | Significado |
|---|---|
| MATNR | Código do material no SAP (chave de sincronização). |
| MIGO | Transação de movimentação de mercadorias no SAP. |
| MM03 | Exibição do cadastro mestre de material. |
| Centro (Plant) | Unidade organizacional de estoque no SAP. |
| Depósito (Storage Location) | Subdivisão de estoque dentro de um centro. |
| Movimento 311 | Transferência entre depósitos do mesmo centro. |
| Movimento 301 | Transferência entre centros (uma etapa). |
| Movimento 261 | Saída para Ordem (consumo por ordem de manutenção). |
| Movimento 201 | Saída para Centro de Custo. |
| Documento de material | Comprovante gerado pelo SAP a cada movimento. |

## Termos técnicos do projeto

| Termo | Significado |
|---|---|
| ORM | Mapeamento objeto-relacional (SQLAlchemy). |
| DTO | Objeto de transporte de dados (Pydantic). |
| Upsert | Atualiza se existe, cria se não existe. |
| Contagem cega | Inventário sem mostrar o saldo do sistema a quem conta. |
| SELECT ... FOR UPDATE | Trava a linha para evitar concorrência no saldo. |
| Sessão (# region) | Bloco de organização do código (padrão Sentinel). |
