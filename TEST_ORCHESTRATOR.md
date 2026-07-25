# Testando o Orchestrator da Bruna

## O que mudou?

A Bruna agora usa um **router inteligente** que decide automaticamente a melhor estratégia:

### Antes
```
Pergunta → RAG → LLM → Resposta
```
(sempre o mesmo fluxo)

### Agora
```
Pergunta → Router (classifica intent)
    ├─ Buscar processo? → Agent + tool buscar_processo
    ├─ Verificar prazo? → Agent + tool verificar_prazo  
    ├─ Buscar cliente?  → Agent + tool buscar_cliente
    ├─ Calcular prazo?  → Agent + tool calcular_prazo
    └─ Geral/jurídico?  → Chain (RAG + LLM)
```

## Exemplos de perguntas e estratégia escolhida

| Pergunta | Estratégia | Por quê |
|----------|-----------|---------|
| "Qual o prazo para contestar?" | Chain (RAG) | Genérico, só precisa de RAG |
| "Busca o processo 0001234-56.2024.8.26.0100" | **Agent + tool** | Precisa consultar o sistema |
| "Me mostra os prazos vencendo essa semana" | **Agent + tool** | Precisa consultar módulo de Prazos |
| "Como funciona a LGPD?" | Chain (RAG) | Pesquisa jurídica na base |
| "Calcula prazo a partir de 15/01/2024" | **Agent + tool** | Usa tool calcular_prazo |
| "Busca o cliente João Silva" | **Agent + tool** | Precisa consultar banco de dados |

## Como testar

### 1. Testar no Swagger

```
POST http://localhost:8090/v1/assistant/bruna/chat
```

Body:
```json
{
  "message": "Busca o processo 0001234-56.2024.8.26.0100",
  "history": [],
  "use_rag": true,
  "escritorio_id": "default"
}
```

### 2. Testar diferentes cenários

#### Pergunta genérica (usa chain)
```json
{
  "message": "Qual é o prazo para contestar uma ação cível?",
  "history": [],
  "use_rag": true
}
```

**Resultado esperado:**
- Estratégia: `chain`
- Intent: `pesquisa_juridica`
- Resposta: vem do RAG (CPC art. 335)

#### Busca de processo (usa agent)
```json
{
  "message": "Me mostra informações do processo 0001234-56",
  "history": []
}
```

**Resultado esperado:**
- Estratégia: `agent`
- Intent: `buscar_processo`
- Tool usada: `buscar_processo`
- Resposta: dados do sistema (se processo existir)

#### Prazos vencendo (usa agent)
```json
{
  "message": "Quais prazos vencem nos próximos 7 dias?",
  "history": []
}
```

**Resultado esperado:**
- Estratégia: `agent`
- Intent: `verificar_prazo`
- Tool usada: `listar_prazos_proximos`

## Metadados na resposta

A resposta agora inclui metadados sobre a estratégia escolhida:

```json
{
  "answer": "...",
  "assistant": "bruna",
  "_metadata": {
    "strategy": "agent",
    "intent": "buscar_processo",
    "explanation": "Detectado número de processo - usando agent",
    "use_agent": true,
    "use_rag": false,
    "tools_used": ["buscar_processo"],
    "iterations": 2
  }
}
```

## Configuração

No `.env`:

```env
# URL da API Java (onde estão os dados reais)
JAVA_API_URL=http://localhost:8082/api
```

## Próximos passos

Com essa base, você pode:

1. **Adicionar mais tools**:
   - `buscar_documentos_processo(id)`
   - `listar_audiencias_proximas()`
   - `buscar_jurisprudencia_tribunal(query)`

2. **Melhorar o router**:
   - Usar LLM para classificar intent (mais preciso)
   - Extrair entidades (nomes, datas, números)

3. **Adicionar memória de sessão**:
   - "Qual o prazo desse processo?" (referência ao último processo mencionado)

4. **LangGraph para fluxos complexos**:
   - Multi-step: buscar processo → verificar prazos → sugerir ação
