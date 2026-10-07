# 📚 Base de Conhecimento — VIA WMS (Índice)

> Ponto de partida da base de conhecimento do projeto **VIA WMS**.
> Sempre que houver evolução relevante, **atualize** o arquivo correspondente
> e registre no `KB_05_CHANGELOG.md`.

---

## Como usar esta base

- Antes de codificar qualquer coisa, o agente deve **ler** os arquivos KB.
- Ao final de cada evolução, o agente deve **atualizar** os arquivos KB.
- Nunca apagar decisões antigas — acrescentar e datar.

## Mapa dos documentos

| Arquivo | Conteúdo |
|---|---|
| `KB_00_INDICE.md` | Este índice e a regra de governança da base. |
| `KB_01_VISAO_GERAL.md` | Objetivo, escopo, personas e visão do produto. |
| `KB_02_MODELO_DADOS.md` | Tabelas ORM, relacionamentos e campos-chave. |
| `KB_03_REGRAS_NEGOCIO.md` | Regras do WMS e mapeamento com o SAP. |
| `KB_04_INTEGRACAO_SAP.md` | Import/Export Excel, movimentos, conciliação. |
| `KB_05_CHANGELOG.md` | Histórico datado de todas as evoluções. |
| `KB_06_BACKLOG.md` | Próximos passos e pendências priorizadas. |
| `KB_07_GLOSSARIO.md` | Termos de negócio (via permanente + SAP). |

## Documentos de regra (fora da pasta KB)

| Arquivo | Conteúdo |
|---|---|
| `regras/REGRA_ABSOLUTA_CODIFICACAO.md` | Padrão obrigatório de código. |
| `instrucoes/INSTRUCOES_AGENTE_CURTO.md` | Instruções para o Copilot Studio. |
| `instrucoes/INSTRUCOES_AGENTE_COMPLETO.md` | Versão completa das instruções. |

---

## ⚙️ REGRA PERMANENTE DE GOVERNANÇA DA BASE

O agente **VIA WMS Copilot** deve, ao final de cada evolução relevante
(novo módulo, mudança de regra, decisão de arquitetura, correção importante,
nova integração), executar automaticamente:

1. Atualizar este índice (`KB_00_INDICE.md`) se surgir novo documento.
2. Atualizar o KB específico do tema alterado.
3. Acrescentar entrada em `KB_05_CHANGELOG.md` com:
   - Data (AAAA-MM-DD).
   - Versão incremental (v0.1.0, v0.1.1...).
   - O que mudou.
   - Arquivos afetados.
   - Motivo/decisão (e a decisão anterior, se foi substituída).
4. Sinalizar ao Julio: **"📌 Base de conhecimento atualizada (vX) — arquivos: ..."**.

> Objetivo: **nunca perder histórico nem evolução** do projeto.

**Versão atual da base:** v0.1.0
**Última atualização:** 2026-08-14
