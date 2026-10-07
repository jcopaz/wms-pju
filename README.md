# 🚆 VIA WMS — Controle de Materiais da Via Permanente

Sistema de **entrada, saída, transferência, custódia e inventário** de materiais
da Via Permanente, com **integração ao SAP via Excel** (import da base / export
de baixa) e **registro pelo celular**. Construído em **Python + Streamlit +
Supabase (Postgres)**, seguindo o mesmo padrão do Painel Sentinel: organização
por **Sessões**, linguagem simples e camadas bem separadas.

---

## 🧱 Arquitetura em camadas

```
┌────────────────────────────────────────────┐
│ UI (Streamlit, mobile-first)               │  ui/pages/*
│  Dashboard, Entrada, Saída, Transferência, │
│  Inventário, Importar SAP, Exportar Baixa  │
├────────────────────────────────────────────┤
│ Serviços (regras de negócio)               │  services/*
│  wms_service, stock_service,               │
│  sap_import_service, sap_export_service,   │
│  analytics_service                         │
├────────────────────────────────────────────┤
│ Models (ORM SQLAlchemy 2)                  │  models/*
├────────────────────────────────────────────┤
│ Core (config + conexão banco)              │  core/*
├────────────────────────────────────────────┤
│ Supabase / PostgreSQL                      │
└────────────────────────────────────────────┘
```

## 📂 Estrutura de pastas

```
via_wms/
├── app.py                     # entrada Streamlit (menu + roteador)
├── requirements.txt
├── .env.example               # copie para .env e preencha
├── core/
│   ├── config.py              # marca, cores, banco, regras SAP, regras WMS
│   └── database.py            # engine + sessão + criar_tabelas()
├── models/                    # 1. SCHEMAS (ORM)
│   ├── base.py  enums.py  organization.py  materials.py
│   ├── partners.py  stock.py  movements.py  custody.py
│   ├── inventory.py  sap_integration.py  __init__.py
├── services/                  # 2/3. REGRAS DE NEGÓCIO + INTEGRAÇÃO SAP
│   ├── stock_service.py       # motor de saldo (com trava de concorrência)
│   ├── wms_service.py         # ENTRADA / SAÍDA / TRANSFERÊNCIA
│   ├── sap_import_service.py  # lê Excel do SAP e sincroniza materiais
│   ├── sap_export_service.py  # gera Excel padronizado de baixa
│   └── analytics_service.py   # KPIs e gráficos do dashboard
├── ui/                        # 4. INTERFACE (UIX)
│   ├── theme.py               # cores, CSS mobile, cabeçalho
│   └── pages/*                # telas
├── scripts/
│   └── seed.py                # cria tabelas + dados de teste
└── assets/
    └── logo.png               # 5. LOGOTIPO
```

## 🔗 Mapeamento com o SAP (movimentos)

| Operação WMS | Condição | Movimento SAP |
|---|---|---|
| Entrada (recebimento) | mesmo centro | **311** |
| Entrada (recebimento) | entre centros | **301** |
| Saída (consumo) | Ordem de Manutenção | **261** |
| Saída (consumo) | Centro de Custo | **201** |
| Estorno | conforme original | 262 / 202 / 312 |

> O número do material usa sempre o **MATNR do SAP** como chave de sincronização.

## ▶️ Como rodar (passo a passo simples)

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Copie o `.env.example` para `.env` e preencha o `DATABASE_URL` do Supabase.
3. Crie as tabelas e dados de teste:
   ```bash
   python scripts/seed.py
   ```
4. Rode o app:
   ```bash
   streamlit run app.py
   ```

## 🔄 Ciclo de integração SAP

1. **Importar** o Excel do SAP → atualiza materiais (`Importar SAP`).
2. Registrar **entradas/saídas** pelo celular.
3. **Exportar** o Excel padronizado de baixa (`Exportar Baixa SAP`).
4. Efetuar a baixa no SAP e **confirmar** o documento de material (conciliação).

## 🛡️ Regras de segurança já embutidas

- Saldo nunca fica negativo (configurável).
- Trava de concorrência (`SELECT ... FOR UPDATE`) evita duas baixas errarem o saldo.
- Toda saída exige objeto de custo (Ordem ou Centro de Custo).
- Movimento concluído é imutável — correção só por estorno.
- Auditoria (`audit_logs`) e anexos (`attachments`) prontos.

## 🚧 Próximos passos sugeridos

- Trocar o login placeholder por **AD/Entra ID**.
- Implementar telas de **custódia** e **conciliação SAP**.
- Migrações com **Alembic**.
- Leitura de **QR Code / código de barras** no celular.
