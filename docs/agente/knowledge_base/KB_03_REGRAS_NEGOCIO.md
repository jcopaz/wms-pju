# KB_03 — Regras de Negócio do WMS

**Versão:** v0.1.0 · **Atualizado em:** 2026-08-14

---

## 1. Entrada (recebimento do Almoxarifado Central)

- Credita saldo no endereço de destino.
- Movimento SAP: **311** (mesmo centro) ou **301** (entre centros).
- Serviço: `wms_service.registrar_entrada`.

## 2. Saída (consumo)

- Debita saldo do endereço de origem (com trava de concorrência).
- Exige **objeto de custo** (Ordem ou Centro de Custo).
- Movimento SAP: **261** (Ordem de Manutenção) ou **201** (Centro de Custo).
- Serviço: `wms_service.registrar_saida`.

## 3. Transferência interna

- Move material entre endereços do mesmo depósito.
- **Não** gera baixa contábil (não consome).
- Serviço: `wms_service.registrar_transferencia`.

## 4. Custódia (a implementar completo)

- Entrega temporária ≠ consumo contábil imediato.
- Controla entregue x consumido x devolvido x perdido.
- Baixa no SAP apenas na **confirmação de consumo**.

## 5. Inventário

- Campanha com cutoff, **contagem cega** por padrão.
- Contagem → recontagem se divergente → aprovação → ajuste.
- Ajuste gera movimento (positivo/negativo) e, se necessário, baixa no SAP.

## 6. Propriedade do material

- `OwnershipType`: MRS, CONTRACTOR, CONSIGNMENT, OTHER.
- Material da contratada **não** entra no saldo patrimonial da MRS.
- CNPJ/contrato são rastreabilidade; o objeto de custo SAP contabiliza.

## 7. Estados dos documentos

- Movimento: RASCUNHO → EM_ANDAMENTO → CONCLUIDO → (AGUARDANDO_SAP →
  CONCILIADO) | CANCELADO | ESTORNADO.
- Custódia: ABERTA → PARCIAL_* → FECHADA_* | DIVERGENTE.
- Inventário: PLANEJADO → ABERTO → CONTANDO → RECONTAGEM →
  AGUARDANDO_APROVACAO → APROVADO → AJUSTADO.

## 8. Regras invioláveis

1. Saldo nunca negativo (salvo parâmetro explícito).
2. `SELECT ... FOR UPDATE` em toda baixa de saldo.
3. Movimento concluído é imutável — correção só por estorno.
4. Toda saída precisa de objeto de custo.
5. Auditoria em operações sensíveis.

## 9. Parâmetros configuráveis (`core/config.py` → WMSRules)

- `bloquear_saldo_negativo` (padrão: True).
- `limite_aprovacao_valor` (padrão: R$ 5.000).
- `exigir_objeto_custo_na_saida` (padrão: True).
- `contagens_inventario` (padrão: 2).
- `inventario_contagem_cega` (padrão: True).
- `movimento_sap` (mapa operação → código SAP).

## 10. Pendências

- Regras de estorno (serviço dedicado).
- Reserva de material antes da entrega.
- Aprovação de saída acima do limite de valor.
