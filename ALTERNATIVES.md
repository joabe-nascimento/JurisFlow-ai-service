# 🔄 Alternativas de LLM — Sem Groq

## Problema: Erro de Login no Groq

Se você não conseguir criar conta no Groq, existem alternativas:

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

1. **Arquivo `.env` já criado** (sem LLM)
2. **Rode o serviço:**
```bash
cd JurisFlow-ai-service
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

3. **Teste no Swagger** (http://localhost:8090/docs):

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

**Você verá:**
- ✅ Retrieval: `langchain`
- ✅ LLM Provider: `groq`
- ⚠️ LLM Cost: `GRÁTIS` (mas sem chave)
- ✅ Vector Store funcionando
- ✅ Busca semântica operacional

---

## 🆓 Opção 2: Outros LLMs Gratuitos

### 2.1 OpenRouter (GRÁTIS com rate limits)
OpenRouter agrega vários providers, alguns gratuitos:

1. Cadastre em: https://openrouter.ai/
2. Pegue API key
3. Mude o `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sua_chave_openrouter
OPENAI_MODEL=meta-llama/llama-3-8b-instruct:free
```

**Models gratuitos no OpenRouter:**
- `meta-llama/llama-3-8b-instruct:free`
- `google/gemma-7b-it:free`
- `mistralai/mistral-7b-instruct:free`

### 2.2 HuggingFace Inference API (GRÁTIS)
HuggingFace oferece API gratuita com rate limits:

1. Cadastre em: https://huggingface.co/
2. Pegue API token em: https://huggingface.co/settings/tokens
3. Instale:
```bash
pip install huggingface_hub
```

4. Adapte o código (vou criar exemplo abaixo)

### 2.3 Ollama (LOCAL, GRÁTIS, SEM API)
Roda LLMs no seu PC:

1. Baixe: https://ollama.ai/
2. Instale e rode:
```bash
ollama pull llama3
ollama serve
```
3. Mude `.env`:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3
```
4. Mude `app/llm/provider.py`:
```python
return ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="llama3"
)
```

---

## 🎯 Opção 3: Usar Azure OpenAI (PAGO, mas trial)

Se você tem conta Azure com créditos:

1. Portal Azure: https://portal.azure.com
2. Crie recurso "Azure OpenAI"
3. Deploy um modelo (GPT-4o-mini é mais barato)
4. Pegue endpoint e chave
5. Configure `.env`:
```env
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=sua_chave
AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com
AZURE_DEPLOYMENT_NAME=gpt-4o-mini
```

---

## 🔧 Opção 4: Adaptar para HuggingFace (código)

Vou criar um provider HuggingFace:

**Crie: `app/llm/huggingface_provider.py`**
```python
from langchain_community.llms import HuggingFaceHub
from app.config import settings

def get_huggingface_llm(temperature=0.0):
    """LLM gratuito via HuggingFace Inference API."""
    return HuggingFaceHub(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        huggingfacehub_api_token=settings.huggingface_token,
        model_kwargs={
            "temperature": temperature,
            "max_new_tokens": 512
        }
    )
```

**Atualize `requirements.txt`:**
```
huggingface_hub>=0.20.0
```

**Adicione em `config.py`:**
```python
huggingface_token: str = ""
```

**Use no `.env`:**
```env
HUGGINGFACE_TOKEN=hf_sua_chave
```

---

## 📊 Comparação de Alternativas

| Opção | Custo | Setup | Qualidade | Rate Limit |
|-------|-------|-------|-----------|------------|
| **Groq** | Grátis | Fácil | Alta (Llama 3.3 70B) | Generoso |
| **OpenRouter** | Grátis | Fácil | Média (modelos 7B) | Moderado |
| **HuggingFace** | Grátis | Médio | Média | Restrito |
| **Ollama (local)** | Grátis | Difícil | Alta (local) | Sem limite |
| **Azure** | Pago | Médio | Muito alta | Depende do plano |

---

## 🎯 Recomendação

### Para TESTAR AGORA (sem LLM):
1. Use o `.env` que criei (já está configurado)
2. Rode o serviço
3. Teste os endpoints RAG no Swagger
4. Valide a busca semântica

### Para usar com LLM:
1. Tente Groq novamente em algumas horas
2. Se não der, use OpenRouter (cadastro rápido)
3. Ou instale Ollama (funciona offline)

### Para PRODUÇÃO:
- Azure OpenAI ou provider com SLA adequado

---

## 🧪 Teste Rápido (SEM LLM)

```bash
# 1. Ative ambiente
cd C:\projetos\projeto-unef\JurisFlow-ai-service
.venv\Scripts\activate

# 2. Rode
uvicorn app.main:app --reload --port 8090

# 3. Em outro terminal, teste RAG:
curl -X POST http://localhost:8090/v1/rag/default/seed

curl -X POST http://localhost:8090/v1/rag/default/search \
  -H "Content-Type: application/json" \
  -d '{"query": "LGPD obrigações escritório", "limit": 3}'
```

**Você verá:**
```json
{
  "query": "LGPD obrigações escritório",
  "total_matches": 2,
  "chunks": [
    {
      "document_title": "LGPD - Obrigações para Escritórios",
      "score": 87.5,
      "content": "Política de privacidade..."
    }
  ],
  "retrieval": "langchain-faiss"
}
```

✅ **RAG funcionando sem LLM!**

---

## ❓ FAQ

**P: Funciona sem LLM?**  
R: Sim. RAG, busca semântica e indexação funcionam independentemente. Chains e agents precisam de um provider configurado.

**P: Vale a pena instalar Ollama?**  
R: Se tiver tempo e PC razoável (8GB+ RAM), sim. É a opção mais completa offline.

---

## 🔗 Links Úteis

- **OpenRouter**: https://openrouter.ai/ (MAIS FÁCIL)
- **HuggingFace**: https://huggingface.co/settings/tokens
- **Ollama**: https://ollama.ai/
- **Azure Trial**: https://azure.microsoft.com/free/

---

**Status**: `.env` já criado para você testar RAG SEM LLM agora! 🚀
