# ⚡ COMECE AQUI — JurisFlow AI

## 🎯 O que é?

Motor de IA do JurisFlow com:
- **RAG** (FAISS + embeddings semânticos)
- **3 Chains** (análise de contratos, pesquisa, geração)
- **Agent com 4 Tools** (ReAct pattern)
- **Multi-LLM** (OpenRouter, Azure OpenAI, OpenAI)
- **16 Endpoints** FastAPI

---

## 🚀 Como Rodar (2 passos)

### 1. Instalar
```bash
cd JurisFlow-ai-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Rodar
```bash
uvicorn app.main:app --reload --port 8090
```

Abra: http://localhost:8090/docs

Configure `.env` conforme `.env.example` (OpenRouter, Azure OpenAI ou OpenAI).

**⚠️ Problemas com o provider?** Veja `ALTERNATIVES.md`

---

## 🧪 Testar

### Teste automático (RAG, sem LLM)
```bash
python test_rag_only.py
```

### Swagger
http://localhost:8090/docs

1. `POST /v1/rag/default/seed` → popula base
2. `POST /v1/rag/default/search` → busca semântica

### Agent (precisa LLM configurado)
```bash
python test_agent.py
```

---

## 📚 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| **QUICKSTART.md** | Setup detalhado |
| **README.md** | Arquitetura e endpoints |
| **EXAMPLES.md** | Exemplos práticos |
| **ALTERNATIVES.md** | Outros providers de LLM |

---

## ❓ Dúvidas?

- **Erro ao rodar?** → `QUICKSTART.md` (Troubleshooting)
- **Como funciona?** → `README.md`
- **Exemplos?** → `EXAMPLES.md`

---

**Comece agora:** `uvicorn app.main:app --reload --port 8090`
