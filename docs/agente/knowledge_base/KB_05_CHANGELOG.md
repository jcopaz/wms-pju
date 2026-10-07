# KB_05 — Changelog (histórico de evoluções)

> **Regra permanente:** a cada evolução relevante, acrescente uma entrada no
> topo desta lista. Nunca apague entradas antigas.

Formato de cada entrada:
```
## vX.Y.Z — AAAA-MM-DD
- O que mudou: ...
- Arquivos afetados: ...
- Motivo/decisão: ...
- Decisão anterior substituída (se houver): ...
```

---

## v0.2.0 — 2026-10-07
- O que mudou: login provisório com usuários no banco (`users.password_hash`,
  PBKDF2-SHA256 600 mil iterações, bloqueio após 5 tentativas na sessão);
  script `scripts/criar_usuario.py` para criar/trocar senha/desativar;
  telas de Entrada, Saída, Transferência e Inventário passam a gravar o
  usuário logado (antes enviavam um UUID aleatório, o que violava a FK
  `users.id` e impedia qualquer movimento). Banco passa a ser o Neon.
- Arquivos afetados: app.py, services/auth_service.py (novo),
  scripts/criar_usuario.py (novo), ui/pages/entrada.py, saida.py,
  transferencia.py, inventario.py, README.md, .env.example.
- Motivo/decisão: permitir piloto publicado sem acesso aberto; Supabase da
  org Free já está no limite.
- Decisão anterior substituída: login placeholder que aceitava qualquer senha.

## v0.1.0 — 2026-08-14
- O que mudou: criação inicial do projeto VIA WMS (esqueleto completo).
  - Camadas: core, models, services, ui, scripts.
  - Módulos ORM: organização, materiais, parceiros, estoque, movimentos,
    custódia, inventário, integração SAP, auditoria.
  - Serviços: stock_service (motor de saldo com trava de concorrência),
    wms_service (entrada/saída/transferência), sap_import_service,
    sap_export_service, analytics_service.
  - UI Streamlit mobile-first: dashboard, entrada, saída, transferência,
    inventário, importar_sap, exportar_sap + tema.
  - Logotipo VIA WMS (navy + âmbar).
  - Governança do agente: instruções (curta/completa), Regra Absoluta de
    codificação e base de conhecimento (KB_00 a KB_07).
- Arquivos afetados: projeto inteiro (32 arquivos .py + KB + regras).
- Motivo/decisão: estruturar o WMS seguindo o padrão do Painel Sentinel
  (organização por Sessões, linguagem simples, Supabase, mobile-first).
- Decisão anterior substituída: nenhuma (primeira versão).
