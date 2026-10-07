# ⛔ REGRA ABSOLUTA DE CODIFICAÇÃO — VIA WMS

> Documento oficial. Vale para o agente, para o Claude Code e para qualquer
> assistente que gere código neste projeto. **Inviolável.**

---

## 1. Princípio

Todo código entregue deve ser **completo, funcional e pronto para rodar**.
Nada de "esboço", "exemplo parcial" ou "depois a gente completa".

## 2. Proibições (nunca fazer)

| ❌ Proibido | Por quê |
|---|---|
| Reticências `...` representando código omitido | Quebra o arquivo, gera erro |
| Comentários "resto do código aqui", "igual ao anterior" | Perde funções |
| `TODO`, `FIXME` como substituto de lógica real | Deixa o módulo incompleto |
| `pass` vazio no lugar de implementação | Função não faz nada |
| Entregar só "as partes que mudaram" sem contexto suficiente | Ambiguidade |
| Funções sem tipo de retorno/parâmetros | Perde tipagem |
| Classe/método sem docstring | Perde documentação |
| Operação sem log | Perde rastreabilidade |

## 3. Obrigações (sempre fazer)

### 3.1 Módulos completos
- Escreva o arquivo inteiro, do `import` ao final.
- Se for muito grande, **quebre em micro-sessões numeradas** (7.2.1.1,
  7.2.1.2...) e entregue todas — mas cada trecho é código real.

### 3.2 Tipagem completa
- `from __future__ import annotations` no topo.
- Tipos em todos os parâmetros e retornos.
- Use `Optional`, `list`, `dict`, tipos de domínio e Enums quando aplicável.

### 3.3 Pydantic v2 para dados
- DTOs de entrada/saída dos serviços em `BaseModel`.
- Validações com `field_validator` / `model_validator`.
- `model_config = ConfigDict(from_attributes=True)` quando ler do ORM.

### 3.4 Docstrings em tudo
- Toda classe e todo método/função com docstring em português, formato:
  ```
  """Explica o que faz.

  Args:
      x: ...
  Returns:
      ...
  """
  ```

### 3.5 Logs detalhados
- Um `logger = logging.getLogger(__name__)` por módulo.
- `logger.info` no início e fim de operações (com número do documento, MATNR,
  quantidade, depósito).
- `logger.warning` para atenção (saldo baixo, divergência de inventário).
- `logger.error("...", exc_info=True)` dentro de `except`.
- **Nunca** logar senha, token ou string de conexão.

## 4. Modelo de referência (como deve ser todo serviço)

```python
from __future__ import annotations

import logging
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class EntradaItemDTO(BaseModel):
    """Item de uma entrada de material.

    Args:
        material_id: identificador do material.
        quantidade: quantidade recebida (maior que zero).
    """

    model_config = ConfigDict(from_attributes=True)

    material_id: str = Field(..., description="ID do material (UUID em texto).")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade recebida.")

    @field_validator("quantidade")
    @classmethod
    def _valida_quantidade(cls, valor: Decimal) -> Decimal:
        """Garante que a quantidade é positiva.

        Args:
            valor: quantidade informada.
        Returns:
            A mesma quantidade, se válida.
        """
        if valor <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        return valor


def registrar_entrada(item: EntradaItemDTO) -> str:
    """Registra a entrada de um item no estoque local.

    Args:
        item: dados validados do item de entrada.
    Returns:
        O número do documento de movimento gerado.
    """
    logger.info(
        "Iniciando entrada | material=%s quantidade=%s",
        item.material_id,
        item.quantidade,
    )
    try:
        numero_documento = "ENT-EXEMPLO-0001"
        logger.info("Entrada concluída | documento=%s", numero_documento)
        return numero_documento
    except Exception:
        logger.error("Falha ao registrar entrada", exc_info=True)
        raise
```

> Observação: o exemplo acima é um **arquivo válido e completo**. Nenhuma
> parte foi substituída por reticências. Esse é o padrão esperado.

## 5. Checklist antes de entregar qualquer módulo

- [ ] Arquivo completo, sem `...` e sem "resto aqui".
- [ ] Todas as funções previstas estão presentes.
- [ ] Tipagem em todas as assinaturas.
- [ ] Pydantic nos dados de entrada/saída.
- [ ] Docstring em cada classe e método.
- [ ] Logs INFO/WARNING/ERROR nos pontos certos.
- [ ] Sem segredos no código.
- [ ] Base de conhecimento atualizada (se houve evolução).
