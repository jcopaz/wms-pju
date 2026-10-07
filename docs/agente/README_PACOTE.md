# 📦 Pacote de Governança do Agente — VIA WMS

Este pacote contém tudo para você configurar o agente **VIA WMS Copilot** no
Copilot Studio e manter a base de conhecimento sempre atualizada.

## Conteúdo

```
via_wms_agente/
├── instrucoes/
│   ├── INSTRUCOES_AGENTE_CURTO.md      # cole no campo "Instructions" (4.550 chars)
│   ├── INSTRUCOES_AGENTE_COMPLETO.md   # versão longa / referência da equipe
│   ├── DESCRICAO_AGENTE.md             # cole no campo "Description"
│   └── PROMPT_INICIAL_STARTER.md       # 1ª mensagem para ativar o agente
├── regras/
│   └── REGRA_ABSOLUTA_CODIFICACAO.md   # padrão obrigatório de código
└── knowledge_base/
    ├── KB_00_INDICE.md
    ├── KB_01_VISAO_GERAL.md
    ├── KB_02_MODELO_DADOS.md
    ├── KB_03_REGRAS_NEGOCIO.md
    ├── KB_04_INTEGRACAO_SAP.md
    ├── KB_05_CHANGELOG.md
    ├── KB_06_BACKLOG.md
    └── KB_07_GLOSSARIO.md
```

## Passo a passo no Copilot Studio

1. **Criar o agente** (Sandbox Maker): dê o nome **VIA WMS Copilot**.
2. **Description:** cole o texto de `instrucoes/DESCRICAO_AGENTE.md`.
3. **Instructions:** cole `instrucoes/INSTRUCOES_AGENTE_CURTO.md`
   (cabe no limite ~8.000 caracteres).
4. **Knowledge:** faça upload dos 8 arquivos `KB_*.md` e do
   `REGRA_ABSOLUTA_CODIFICACAO.md`.
5. **Primeira conversa:** cole `instrucoes/PROMPT_INICIAL_STARTER.md`.
6. Pronto — o agente já opera com as regras e a governança da base.

## Como a base se mantém viva

A cada evolução (novo módulo, mudança de regra, decisão), o agente deve:
1. Atualizar o KB do tema + `KB_00_INDICE.md`.
2. Registrar em `KB_05_CHANGELOG.md` (data, versão, o que mudou, motivo).
3. Avisar: **"📌 Base de conhecimento atualizada (vX)"**.

Você então baixa os KB atualizados e faz novo upload no conhecimento do agente
(ou usa uma fonte conectada, como SharePoint/Dataverse, se disponível).

## Dica de continuidade

Mantenha estes arquivos versionados junto do código (mesmo repositório GitHub),
na pasta `docs/agente/`. Assim, código e conhecimento evoluem juntos.
