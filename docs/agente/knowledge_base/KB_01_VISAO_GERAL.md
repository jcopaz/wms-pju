# KB_01 — Visão Geral do VIA WMS

**Versão:** v0.1.0 · **Atualizado em:** 2026-08-14

---

## 1. O que é

O **VIA WMS** é um sistema de gestão de estoque local (Warehouse Management
System) para as coordenações de **Via Permanente** da MRS Logística. Ele
controla a **entrada, saída, transferência, custódia e inventário** de
materiais e conversa com o **SAP** por meio de planilhas Excel (importação da
base e exportação padronizada para baixa).

## 2. Problema que resolve

Hoje o controle de material na ponta é manual/planilha, sem rastreabilidade
fina (quem pegou, para qual ordem, quanto sobrou) e sem integração fluida com
o SAP. Isso gera divergência de estoque, retrabalho e baixa auditabilidade.

## 3. Objetivos

- Registrar movimentações **pelo celular**, no campo, com foto e localização.
- Diferenciar entregas a **colaboradores próprios** e a **prestadores**
  (contrato + CNPJ).
- Vincular consumo ao **objeto de custo** correto (Ordem 261 / Centro 201).
- **Importar** a base SAP em Excel e **exportar** as baixas em layout padrão.
- **Inventariar** de forma automatizada, com contagem cega e conciliação.
- Oferecer **dashboard** de análise (KPIs, consumo, saldo por depósito).

## 4. Personas

| Persona | Necessidade principal |
|---|---|
| Almoxarife local | Receber, guardar, entregar e devolver material rápido. |
| Equipe de manutenção | Pegar material para uma ordem, no campo. |
| Fiscal de contrato | Validar entrega para a contratada. |
| Coordenador | Ver saldo, consumo e divergências. |
| Responsável SAP | Baixar no SAP e conciliar documentos. |
| Auditor | Consultar histórico sem alterar nada. |

## 5. Escopo do MVP

- Cadastro de materiais via import SAP.
- Entrada, Saída e Transferência.
- Exportação de baixa para o SAP.
- Dashboard básico.
- Inventário (abertura de campanha + contagem).

## 6. Fora do MVP (próximas ondas)

- Custódia completa (entrega temporária, devolução, perda).
- Conciliação automática do documento de material do SAP.
- Login AD/Entra ID.
- Leitura de QR Code / código de barras.
- Migrações com Alembic.

## 7. Stack técnica

- **Python 3.12**, **Streamlit** (mobile-first).
- **SQLAlchemy 2** + **Pydantic v2**.
- **Supabase / PostgreSQL** (região sa-east-1).
- Excel via **pandas** + **openpyxl**.

## 8. Identidade visual

- Nome: **VIA WMS**.
- Cores: navy `#0B2545` + âmbar de sinalização `#F2A900`.
- Ícone: 🚆 (trilho + caixas + pin de localização).
