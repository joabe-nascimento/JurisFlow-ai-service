# 🤖 JurisFlow AI Service

**Motor de Inteligência Artificial Jurídica** — LangChain + RAG + Agents + LLMs

Stack Python para JurisFlow com foco em **Engenharia de IA** moderna: Retrieval-Augmented Generation, Chains, Agents com Tools e integração com LLMs.

---

## 📐 Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌──────────────────────┐
│  Next.js    │ ───> │ Spring Boot  │ ───> │ FastAPI + LangChain  │
│  (Frontend) │      │  (API Java)  │      │  (Python AI Service) │
└─────────────┘      └──────────────┘      └──────────────────────┘
                                                     │
                     ┌───────────────────────────────┴─────────────┐
                     │                                               │
                ┌────▼────┐  ┌────────┐  ┌────────┐  ┌───────────────┐│
                │   RAG   │  │ Chains │  │ Agents │  │     LLMs      ││
                │  FAISS  │  │        │  │ Tools  │  │ (OpenRouter/  ││
                │         │  │        │  │        │  │  Azure OpenAI)││
                └─────────┘  └────────┘  └────────┘  └───────────────┘│
                                                                     │
                                            Embeddings (local)  ─────┘
```

---

## 🎯 Capacidades

### 1️⃣ **RAG (Retrieval-Augmented Generation)**
- **Vector Store**: FAISS (local, gratuito)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (CPU, gratuito)
- **Chunking**: RecursiveCharacterTextSplitter (LangChain)
- **Retrieval**: Busca semântica com score de similaridade

### 2️⃣ **Chains (Cadeias de Raciocínio)**
- **Contract Analysis**: Analisa contratos e identifica cláusulas de risco
- **Legal Research**: Pesquisa jurídica fundamentada em RAG
- **Document Generation**: Gera minutas de documentos jurídicos

### 3️⃣ **Agents com Tools (ReAct Pattern)**
Agente inteligente com acesso a tools especializadas:
- `calcular_prazo`: Calcula prazos processuais (corridos/úteis)
- `buscar_conhecimento`: Busca semântica no RAG
- `buscar_jurisprudencia`: Busca jurisprudência (simulado, integrável com APIs de tribunais)
- `calcular_honorarios`: Calcula honorários conforme Tabela OAB

### 4️⃣ **LLMs (Language Models)**

---

## 🚀 Deploy em Produção

### 📦 Opções de Deploy

#### 1. **HostGator cPanel** (Shared Hosting)
Deploy via workaround com Setup Python App + nohup + reverse proxy.

📖 **[Ver guia completo: DEPLOY_HOSTGATOR.md](./DEPLOY_HOSTGATOR.md)**

**Vantagens:**
- ✅ Usa hospedagem que você já paga
- ✅ Sem custos adicionais
- ✅ Controle total via cPanel

**Desvantagens:**
- ⚠️ Configuração manual complexa
- ⚠️ Sem auto-deploy
- ⚠️ Processo pode cair após restart do servidor

---

#### 2. **Railway.app** (Recomendado)
Deploy automático via Git com $5/mês de crédito grátis.

📖 **[Ver guia completo: DEPLOY_RAILWAY.md](./DEPLOY_RAILWAY.md)**

**Vantagens:**
- ✅ Deploy em 5 minutos
- ✅ Auto-deploy via Git
- ✅ SSL/HTTPS automático
- ✅ Logs em tempo real
- ✅ Restart automático
- ✅ $5/mês GRÁTIS (suficiente para hobby projects)

**Desvantagens:**
- ⚠️ Custo extra se exceder free tier (~$5-10/mês)

---

#### 3. **Render.com** (Alternativa)
Similar ao Railway, com free tier (mas com sleep após 15min de inatividade).

**Vantagens:**
- ✅ Free tier permanente
- ✅ Auto-deploy via Git

**Desvantagens:**
- ⚠️ Cold start de 30-60s após inatividade
- ⚠️ Não ideal para produção crítica

---

### 🎯 Recomendação

| Cenário | Recomendação |
|---------|--------------|
| **Produção séria** | Railway.app |
| **Economia máxima** | HostGator cPanel |
| **Teste/Staging** | Render.com (free tier) |

---

### 4️⃣ **LLMs (Language Models)**
- **OpenRouter (GRÁTIS/PAGO)**: modelos `:free` — ideal para desenvolvimento
- **Azure OpenAI (PAGO)**: GPT-4o — para produção (também usado como fallback automático)
- **OpenAI (PAGO)**: GPT-4o-mini — alternativa

---

## 🚀 Setup

### 1. Criar ambiente virtual
```bash
cd JurisFlow-ai-service
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar LLM (OpenRouter grátis)
1. Obtenha sua API key grátis em: https://openrouter.ai/keys
2. Copie `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edite `.env` e adicione sua chave:
   ```env
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-v1-your_key_here
   RETRIEVAL_METHOD=langchain
   ```

### 4. Rodar o serviço
```bash
uvicorn app.main:app --reload --port 8090
```

Acesse:
- **API Docs**: http://localhost:8090/docs (Swagger interativo)
- **Health**: http://localhost:8090/health
- **Status**: http://localhost:8090/v1/status

---

## 📡 Endpoints

### **Status & Health**
- `GET /health` — Health check
- `GET /v1/status` — Status completo (LLM, RAG, capabilities)

### **RAG (Knowledge Base)**
- `GET /v1/rag/{escritorio_id}/documents` — Lista documentos
- `POST /v1/rag/{escritorio_id}/documents` — Adiciona documento
- `DELETE /v1/rag/{escritorio_id}/documents/{doc_id}` — Remove documento
- `POST /v1/rag/{escritorio_id}/search` — Busca semântica
- `POST /v1/rag/{escritorio_id}/seed` — Popula base inicial

### **Chains (LangChain)**
- `POST /v1/chains/contract-analysis` — Analisa contratos
  ```json
  {
    "contract_text": "CONTRATO DE...",
    "escritorio_id": "default"
  }
  ```

- `POST /v1/chains/legal-research` — Pesquisa jurídica
  ```json
  {
    "question": "Qual o prazo para contestação no CPC?",
    "escritorio_id": "default"
  }
  ```

- `POST /v1/chains/document-generation` — Gera documentos
  ```json
  {
    "document_type": "Petição Inicial",
    "data": "{\"autor\": \"João\", \"reu\": \"Empresa X\"}",
    "escritorio_id": "default"
  }
  ```

### **Agent (ReAct com Tools)**
- `POST /v1/agent/ask` — Pergunta para o agente
  ```json
  {
    "question": "Qual o prazo para apelar? Hoje é 15/01/2024",
    "escritorio_id": "default",
    "mode": "full"
  }
  ```
  
  Exemplos de perguntas:
  - "Calcule honorários para ação cível de R$ 100.000"
  - "Busque informações sobre LGPD na base de conhecimento"
  - "Qual o prazo de contestação a partir de 10/02/2024?"

---

## 🧠 Como funciona

### RAG com LangChain
```python
from app.rag.langchain_store import langchain_rag_store

# Adicionar documento
doc = langchain_rag_store.add_document("escritorio-1", {
    "title": "CPC - Prazos",
    "content": "Contestação: 15 dias úteis...",
    "category": "Processual"
})

# Buscar (semantic search)
result = langchain_rag_store.search("escritorio-1", "prazo contestação", limit=5)
# Retorna chunks ordenados por similaridade
```

### Chains
```python
from app.chains.contract_analysis import analyze_contract

# Análise de contrato
analysis = await analyze_contract(
    escritorio_id="escritorio-1",
    contract_text="CONTRATO DE PRESTAÇÃO DE SERVIÇOS..."
)
# Retorna relatório estruturado com riscos identificados
```

### Agents
```python
from app.agents.legal_assistant import run_agent

# Agente com tools
result = await run_agent(
    question="Qual prazo para apelar? Hoje é 01/02/2024",
    escritorio_id="escritorio-1"
)
# Agent usa tool calcular_prazo e retorna resposta
```

---

## 📊 Evolução Futura

| Atual | Próximo |
|-------|---------|
| FAISS local | **pgvector** (PostgreSQL) ou **Azure AI Search** |
| Embeddings locais | **Azure OpenAI Embeddings** (ada-002) |
| Agents custom | **LangGraph** (workflows complexos) |
| OpenRouter free tier | **Azure OpenAI** em produção |
| Jurisprudência simulada | **API STJ/STF** (tribunais oficiais) |
| Pipeline simples | **Multi-agent orchestration** (LangGraph) |

---

## 🔗 Integração com JurisFlow

### Java API ➔ Python Service
```java
// PythonAIService.java
public SearchResult search(String escritorioId, String query) {
    return restTemplate.postForObject(
        pythonUrl + "/v1/rag/" + escritorioId + "/search",
        new SearchRequest(query, 5),
        SearchResult.class
    );
}
```

### Frontend ➔ Java API ➔ Python
```typescript
// aiService.ts
export const analyzeContract = async (contractText: string) => {
  return api.post('/v1/integrations/ai/contract-analysis', {
    contractText
  });
};
```

---

## 📝 Variáveis de Ambiente

Ver `.env.example` para configuração completa.

**Mínimo necessário:**
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your_key_here  # https://openrouter.ai/keys
RETRIEVAL_METHOD=langchain
```

---

## 🧪 Testando

### 1. Via Swagger UI
- Acesse http://localhost:8090/docs
- Teste os endpoints interativamente

### 2. Via curl
```bash
# Status
curl http://localhost:8090/v1/status

# Seed inicial
curl -X POST http://localhost:8090/v1/rag/default/seed

# Busca
curl -X POST http://localhost:8090/v1/rag/default/search \
  -H "Content-Type: application/json" \
  -d '{"query": "LGPD", "limit": 3}'

# Agent
curl -X POST http://localhost:8090/v1/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual o prazo para contestação?", "mode": "full"}'
```

---

## 💡 Stack técnica

- **RAG** — FAISS, embeddings locais, busca semântica
- **LangChain** — chains, agents ReAct e tools customizadas
- **LLMs** — OpenRouter, Azure OpenAI e OpenAI via abstração multi-provider
- **Arquitetura** — microserviço Python integrado ao backend Java via REST

---

## 👨‍💻 Autor

Parte do ecossistema **JurisFlow** — plataforma de gestão jurídica com IA.

---

## 📚 Referências

- [LangChain Docs](https://python.langchain.com/)
- [OpenRouter API (Free tier)](https://openrouter.ai/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**Status**: ✅ Pronto para produção (configurar LLM pago e vector DB persistente)
