# KB_06 — Backlog (próximos passos)

**Versão:** v0.1.0 · **Atualizado em:** 2026-08-14

> Prioridade: 🔴 alta · 🟡 média · 🟢 baixa

---

## Curto prazo

- 🔴 Criar **DTOs Pydantic** para entrada/saída de todos os serviços
  (conforme Regra Absoluta).
- 🔴 Adicionar **logging** detalhado em todos os serviços já existentes.
- 🔴 Tela de **custódia** completa (entrega temporária, devolução, perda).
- 🔴 Tela de **conciliação SAP** (confirmar documento de material → POSTADO).
- 🟡 Validar nomes reais das colunas do export SAP da MRS (`SAPSettings`).

## Médio prazo

- 🟡 Login **AD/Entra ID** (substituir placeholder).
- 🟡 Migrações com **Alembic** (substituir `criar_tabelas()`).
- 🟡 Serviço de **estorno** (262/202/312) com rastreabilidade.
- 🟡 **Reserva** formal de material antes da entrega.
- 🟡 Aprovação de saída acima do `limite_aprovacao_valor`.

## Longo prazo

- 🟢 Leitura de **QR Code / código de barras** no celular.
- 🟢 Integração automatizada com SAP via **BAPI/RFC/IDoc/API**.
- 🟢 Preenchimento das **coordenadas** dos depósitos (mapa de calor / geo).
- 🟢 Relatórios exportáveis (PDF/Excel) para auditoria.
- 🟢 Notificações de divergência de inventário.

## Perguntas a validar em campo

- Cada coordenação tem depósito próprio no SAP?
- Almoxarifado e coordenação estão no mesmo centro SAP?
- Transferência em uma ou duas etapas?
- Todo consumo de manutenção tem ordem? Quando 201 é permitido?
- Como são tratados materiais de terceiros e sobras/perdas?
