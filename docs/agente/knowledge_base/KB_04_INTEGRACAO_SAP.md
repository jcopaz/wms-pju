# KB_04 — Integração com o SAP

**Versão:** v0.1.0 · **Atualizado em:** 2026-08-14

---

## 1. Estratégia geral

O SAP continua sendo o sistema **oficial** de estoque e contabilidade. O VIA
WMS é a camada **operacional** (rastreabilidade, celular, endereço, custódia,
inventário). A conversa entre os dois é feita por **Excel**:

- **Importação:** o SAP exporta a base (cadastro/estoque) em Excel → o WMS lê
  e sincroniza os materiais.
- **Exportação:** o WMS gera um Excel **padronizado de baixa** com as saídas →
  alguém executa a baixa no SAP → o documento de material volta para o WMS.

## 2. Importação (`services/sap_import_service.py`)

- `ler_excel()` lê como texto (dtype=str) para não perder zeros do MATNR.
- `sincronizar_materiais()` faz **upsert** por MATNR (cria ou atualiza),
  nunca apaga.
- `registrar_lote()` grava um `SAPImportBatch` para auditoria.
- Nomes das colunas configuráveis em `core/config.py → SAPSettings`
  (ajustar aos nomes reais do export do SAP da MRS).

## 3. Exportação de baixa (`services/sap_export_service.py`)

- `gerar_excel_baixa()` junta todos os `SAPPosting` com status **PENDENTE**.
- Colunas do arquivo: Documento_WMS, Data, Tipo_Movimento_SAP, Material_SAP,
  Descricao, Quantidade, Objeto_Custo, Ordem_Servico, Local_Via, ID_Posting.
- `marcar_exportado()` muda o status para **EXPORTADO** (evita duplicidade).
- `confirmar_baixa()` recebe o documento de material + ano fiscal e marca
  como **POSTADO**.

## 4. Movimentos SAP usados

| Operação WMS | Condição | SAP |
|---|---|---|
| Entrada | mesmo centro | 311 |
| Entrada | entre centros | 301 |
| Saída | Ordem de Manutenção | 261 |
| Saída | Centro de Custo | 201 |
| Estorno | conforme original | 262 / 202 / 312 |

## 5. Ciclo de vida de um `SAPPosting`

```
PENDENTE → EXPORTADO → POSTADO → CONCILIADO
                 ↳ FALHA (com retry_count)
```

## 6. Conciliação (a implementar)

- Comparar `SAPPosting` POSTADO com o documento de material real do SAP.
- Marcar `CONCILIADO` quando material, quantidade e objeto de custo batem.
- Marcar `DIVERGENTE` quando não batem, gerando alerta no dashboard.

## 7. Evolução futura da integração

- Fase 1 (atual): **conciliação assistida** por Excel.
- Fase 2: integração automatizada por **BAPI/RFC/IDoc ou API** autorizada.
- Idempotência: cada movimento gera no máximo um documento de material.

## 8. Pendências

- Tela de conciliação (confirmar documento de material).
- Validação das colunas reais do export SAP da MRS.
- Tratamento de erros de baixa (fila de reprocessamento).
