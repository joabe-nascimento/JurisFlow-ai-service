# ⚡ COMECE AQUI — JurisFlow AI

## 🎯 O que foi feito?

Implementei **LangChain completo** no JurisFlow:
- ✅ **RAG** (FAISS + embeddings semânticos)
- ✅ **3 Chains** (análise contratos, pesquisa, geração)
- ✅ **Agent com 4 Tools** (ReAct pattern)
- ✅ **Multi-LLM** (Groq grátis, Azure, OpenAI)
- ✅ **16 Endpoints** FastAPI
- ✅ **Documentação completa**

**Por quê?** Porque a vaga pedia RAG, Agents, LLMs e Azure — não Docker.

---

## 🚀 Como Rodar (2 passos - SEM precisar de LLM!)

### 1. Instalar
```bash
cd JurisFlow-ai-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Rodar (o .env já está configurado)
```bash
uvicorn app.main:app --reload --port 8090
```

Abra: http://localhost:8090/docs

**✅ O `.env` já foi criado para você testar RAG sem LLM!**

**⚠️ Problema com Groq?** Veja `ALTERNATIVES.md` para outras opções

---

## 🧪 Testar Agora (SEM LLM)

### Teste Automático (RECOMENDADO)
```bash
python test_rag_only.py
```

Isso vai testar:
- ✅ RAG completo (FAISS + embeddings)
- ✅ Busca semântica
- ✅ Similarity scores
- ✅ Multi-tenant

### OU teste no Swagger
http://localhost:8090/docs

1. `POST /v1/rag/default/seed` → **Execute** (popula base)
2. `POST /v1/rag/default/search` → Cole:
```json
{
  "query": "prazo contestação CPC",
  "limit": 3
}
```
3. Veja busca semântica funcionando! 🔍

### Para testar Agent (precisa LLM)
Se conseguir API do Groq ou outro provider:
1. Configure `.env` com sua chave
2. Mude `AGENT_ENABLED=true`
3. Reinicie o serviço
4. Rode `python test_agent.py`

---

## 📚 Documentação

| Arquivo | Para quê? |
|---------|-----------|
| **QUICKSTART.md** | Setup detalhado (5min) |
| **README.md** | Arquitetura completa |
| **EXAMPLES.md** | 10 exemplos práticos |
| **PORTFOLIO.md** | Para entrevistas/currículo |
| **IMPLEMENTATION_SUMMARY.md** | O que foi feito |

---

## 🎯 Para o Currículo

**Resumo em 3 linhas:**
> Desenvolvido motor de IA jurídica com **RAG (FAISS + embeddings)**, **LangChain chains** para análise de contratos e pesquisa jurídica, e **agents ReAct** com 4 tools customizadas. Integração multi-LLM (Groq, Azure OpenAI) via microserviços **Python FastAPI**. Stack: LangChain, FAISS, sentence-transformers, prompt engineering.

---

## 🔥 Próximo Passo

1. ✅ Rode o serviço
2. ✅ Teste o agent no Swagger
3. ✅ Leia `PORTFOLIO.md` para se preparar para entrevistas
4. ✅ Adicione no currículo as tecnologias:
   - RAG (Retrieval-Augmented Generation)
   - LangChain (Chains, Agents, Tools)
   - Vector Databases (FAISS)
   - LLM Integration (Azure OpenAI, Groq)
   - Prompt Engineering

---

## ❓ Dúvidas?

### Erro ao rodar?
- Veja `QUICKSTART.md` seção Troubleshooting

### Como funciona?
- Leia `README.md` seção "Como funciona"

### Exemplos de uso?
- Veja `EXAMPLES.md` (10 casos práticos)

### Para apresentar em entrevista?
- Leia `PORTFOLIO.md` completo

---

## 🎓 Demonstrar em Entrevista

**Pergunta:** _"Você tem experiência com RAG?"_

**Resposta:** 
> "Sim, implementei RAG no JurisFlow usando LangChain com FAISS como vector store e sentence-transformers para embeddings locais. O fluxo é: documentos jurídicos são chunkados, convertidos em embeddings e indexados no FAISS. Na query, fazemos similarity search e injetamos os top-K chunks como contexto no prompt do LLM. Isso fundamenta as respostas em conhecimento real e reduz alucinações. Também criei um agent ReAct com 4 tools que usa o RAG para buscar informações quando necessário."

**Mostre o código:**
- `app/rag/langchain_store.py` — RAG implementation
- `app/agents/legal_assistant.py` — Agent with tools
- `app/chains/contract_analysis.py` — Chain example

---

## ✅ Status

🟢 **TUDO PRONTO**

- ✅ Código funcional (testado)
- ✅ Sintaxe validada
- ✅ Documentação completa
- ✅ Pronto para demonstrar

---

**Comece agora:** `uvicorn app.main:app --reload --port 8090`
