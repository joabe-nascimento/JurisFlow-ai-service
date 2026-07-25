# Changelog - JurisFlow AI Service

## [2.1.0] - Orchestration & Tools de integração (2026-07-25)

### 🚀 Nova funcionalidade: Bruna Inteligente

A Bruna agora usa **orchestration** automática que decide a melhor estratégia para cada pergunta:

#### Antes
- Fluxo fixo: RAG → LLM → resposta
- Não consultava dados reais do sistema

#### Agora
- **Router inteligente** classifica a intenção da pergunta
- **2 estratégias possíveis**:
  - **Chain** (RAG + LLM) — perguntas gerais
  - **Agent + Tools** (ReAct) — ações no sistema

### 🔧 Novas Tools

4 tools que integram com a API Java do JurisFlow:

1. **`buscar_processo(numero)`** — Busca processo no sistema
2. **`listar_prazos_proximos(dias)`** — Prazos vencendo
3. **`buscar_cliente(nome)`** — Informações de cliente
4. **`verificar_prazo_processo(numero)`** — Prazos de um processo específico

### 📂 Arquitetura

```
app/
├── orchestration/         # NOVO
│   ├── router.py          # Classifica intent e decide estratégia
│   └── bruna_orchestrator.py  # Orquestra chain vs agent
├── tools/                 # NOVO
│   └── java_api.py        # Tools que chamam API Java
├── chains/
│   └── bruna_assistant.py # Chain conversacional (existente)
└── agents/
    └── legal_assistant.py # Agent ReAct (existente)
```

### 🎯 Exemplos de comportamento

| Pergunta | Estratégia | Por quê |
|----------|-----------|---------|
| "Qual o prazo para contestar?" | Chain (RAG) | Genérico |
| "Busca o processo 0001234-56" | **Agent + tool** | Consulta sistema |
| "Prazos vencendo essa semana" | **Agent + tool** | Consulta módulo Prazos |
| "Como funciona LGPD?" | Chain (RAG) | Pesquisa jurídica |

### ⚙️ Configuração

Nova variável no `.env`:

```env
JAVA_API_URL=http://localhost:8082/api
```

### 📝 Como testar

Ver arquivo `TEST_ORCHESTRATOR.md` para exemplos completos.

### 🔄 Compatibilidade

- Endpoint `/v1/assistant/bruna/chat` mantém mesma interface
- Resposta inclui metadados sobre estratégia escolhida
- Fallback automático para chain em caso de erro

---

## [2.0.0] - LangChain completo (anterior)

- RAG com FAISS e embeddings
- Chains (análise, pesquisa, geração)
- Agent ReAct com tools
- Multi-LLM (Groq, OpenRouter, Azure, OpenAI)
