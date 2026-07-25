# 🔄 Alternativas de LLM — JurisFlow AI Service

O motor de IA suporta 3 providers: **OpenRouter**, **Azure OpenAI** e **OpenAI**. Groq foi removido do projeto.

---

## ✅ Opção 1: Testar SEM LLM (RECOMENDADO para começar)

**O que funciona sem LLM:**
- ✅ RAG completo (adicionar/buscar documentos)
- ✅ Embeddings semânticos (FAISS)
- ✅ Similarity search
- ✅ Status do serviço
- ✅ Todos endpoints RAG

**O que NÃO funciona:**
- ❌ Chains (análise, pesquisa, geração)
- ❌ Agent (precisa de LLM para raciocinar)

### Como testar só RAG:

1. **Rode o serviço:**
```bash
cd JurisFlow-ai-service
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

2. **Teste no Swagger** (http://localhost:8090/docs):

#### a) Seed inicial
```
POST /v1/rag/default/seed
```

#### b) Buscar documentos
```
POST /v1/rag/default/search
{
  "query": "prazo contestação CPC",
  "limit": 5
}
```

#### c) Ver status
```
GET /v1/status
```

---

## 🆓 Opção 2: OpenRouter (GRÁTIS com rate limits) — recomendado para dev

1. Cadastre em: https://openrouter.ai/keys
2. Pegue a API key
3. Configure o `.env`:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-sua_chave
OPENROUTER_MODEL=openrouter/free
OPENROUTER_FALLBACK_MODELS=google/gemma-4-26b-a4b-it:free,nvidia/nemotron-nano-9b-v2:free,openai/gpt-oss-20b:free
```

Modelos `:free` compartilham um limite diário de ~50 requisições por conta. Se atingir o limite, configure Azure OpenAI ou OpenAI como fallback (veja abaixo).

---

## 🖥️ Opção 3: Ollama (LOCAL, GRÁTIS, SEM API)

Roda LLMs no seu PC, sem depender de rate limit:

1. Baixe: https://ollama.ai/
2. Instale e rode:
```bash
ollama pull llama3
ollama serve
```
3. Configure `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3
```
4. Ajuste `app/llm/provider.py` no branch `openai` para usar `base_url="http://localhost:11434/v1"` quando `OPENAI_API_KEY=ollama`.

---

## 🎯 Opção 4: Azure OpenAI — recomendado para PRODUÇÃO

1. Portal Azure: https://portal.azure.com
2. Crie recurso "Azure OpenAI"
3. Faça deploy de um modelo (ex.: `gpt-4o` ou `gpt-4o-mini`)
4. Pegue endpoint e chave
5. Configure `.env`:
```env
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=sua_chave
AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com
AZURE_DEPLOYMENT_NAME=gpt-4o
```

Com `AZURE_OPENAI_KEY` e `AZURE_OPENAI_ENDPOINT` configurados, o serviço usa Azure automaticamente como **fallback** quando o provider primário (ex.: OpenRouter) atinge o limite diário — sem precisar trocar `LLM_PROVIDER` manualmente (ver `get_provider_attempt_order` em `app/llm/provider.py`).

---

## 🔧 Opção 5: OpenAI direto (PAGO)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## 📊 Comparação

| Opção | Custo | Setup | Qualidade | Rate Limit |
|-------|-------|-------|-----------|------------|
| **OpenRouter (:free)** | Grátis | Fácil | Média | ~50 req/dia |
| **Ollama (local)** | Grátis | Médio | Alta (local) | Sem limite |
| **Azure OpenAI** | Pago | Médio | Muito alta | Depende do plano |
| **OpenAI direto** | Pago | Fácil | Alta | Depende do plano |

---

## 🎯 Recomendação

- **Dev/testes:** OpenRouter (`:free`) — rápido de configurar
- **Dev offline:** Ollama — sem depender de internet/rate limit
- **Produção:** Azure OpenAI — SLA, qualidade e fallback automático do OpenRouter

---

## ❓ FAQ

**P: Funciona sem LLM?**
R: Sim. RAG, busca semântica e indexação funcionam independentemente. Chains e agents precisam de um provider configurado.

**P: O que aconteceu com o Groq?**
R: Foi removido do projeto. Use OpenRouter (dev) ou Azure OpenAI (produção).

---

## 🔗 Links Úteis

- **OpenRouter**: https://openrouter.ai/keys
- **Ollama**: https://ollama.ai/
- **Azure OpenAI**: https://portal.azure.com
