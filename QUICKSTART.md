# 🚀 Guia Rápido — JurisFlow AI Service

## Setup em 5 minutos

### 1. Instalar dependências
```bash
cd JurisFlow-ai-service
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Obter API Key GRATUITA do Groq
1. Acesse: https://console.groq.com/keys
2. Crie uma conta (grátis)
3. Clique em "Create API Key"
4. Copie a chave (começa com `gsk_`)

### 3. Configurar `.env`
```bash
# Copie o exemplo
cp .env.example .env

# Edite .env e adicione sua chave
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_sua_chave_aqui
RETRIEVAL_METHOD=langchain
```

### 4. Rodar
```bash
uvicorn app.main:app --reload --port 8090
```

### 5. Testar
Abra http://localhost:8090/docs e teste os endpoints!

---

## 🧪 Exemplos de Teste (via Swagger)

### 1️⃣ Seed inicial (popular base de conhecimento)
```
POST /v1/rag/default/seed
```

### 2️⃣ Busca semântica
```
POST /v1/rag/default/search
{
  "query": "prazo contestação",
  "limit": 3
}
```

### 3️⃣ Análise de Contrato
```
POST /v1/chains/contract-analysis
{
  "contract_text": "CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n\nCLÁUSULA 1 - DO OBJETO\nA CONTRATADA prestará serviços de desenvolvimento...\n\nCLÁUSULA 5 - DA RESCISÃO\nEste contrato poderá ser rescindido imediatamente pela CONTRATANTE sem aviso prévio...",
  "escritorio_id": "default"
}
```

### 4️⃣ Agente com Tools
```
POST /v1/agent/ask
{
  "question": "Qual o prazo para apelar? A decisão foi publicada em 15/01/2024",
  "escritorio_id": "default",
  "mode": "full"
}
```

Outras perguntas para o agente:
- "Busque informações sobre LGPD"
- "Calcule honorários para ação trabalhista de R$ 80.000"
- "Qual prazo de contestação a partir de 01/03/2024?"

### 5️⃣ Pesquisa Jurídica
```
POST /v1/chains/legal-research
{
  "question": "Quais são os prazos do CPC para recursos?",
  "escritorio_id": "default"
}
```

---

## 📊 Verificar Status
```
GET /v1/status
```

Resposta:
```json
{
  "service": "JurisFlow AI + LangChain",
  "version": "2.0.0",
  "status": "online",
  "retrieval": "langchain",
  "llm_provider": "groq",
  "llm_model": "llama-3.3-70b-versatile",
  "llm_cost": "GRÁTIS",
  "capabilities": [
    "FastAPI",
    "LangChain",
    "RAG (langchain)",
    "FAISS Vector Store",
    "Embeddings locais",
    "Chains (análise, pesquisa, geração)",
    "Agents com Tools",
    "LLM: groq"
  ],
  "escritorios_indexed": 1,
  "total_documents": 6,
  "total_chunks": 12
}
```

---

## 🔥 Dicas

### LLM grátis vs pago
- **Groq (grátis)**: Bom para desenvolvimento. Rate limits generosos.
- **Azure OpenAI (pago)**: Para produção. Melhor qualidade e SLA.

### Performance
- Primeira requisição é lenta (carrega embeddings model)
- Depois fica rápido (~1-3s por request)

### Embeddings
- Rodando em CPU (grátis)
- Se tiver GPU: mude `device: "cuda"` no `langchain_store.py`

### Agente verbose
- Se quiser ver o raciocínio do agent em tempo real:
  ```env
  AGENT_VERBOSE=true
  ```
- No console aparecerá:
  ```
  > Entering new AgentExecutor chain...
  Pensamento: Preciso calcular o prazo...
  Ação: calcular_prazo
  ...
  ```

---

## 🐛 Troubleshooting

### Erro: "groq_api_key não configurada"
- Certifique-se que o `.env` existe e tem `GROQ_API_KEY=gsk_...`
- Reinicie o servidor após editar `.env`

### Erro ao importar FAISS
```bash
pip install faiss-cpu --force-reinstall
```

### Embeddings lentos
- Normal no primeiro uso (baixa o modelo ~80MB)
- Depois fica em cache

### "Tool not found" no agent
- Verifique se `AGENT_ENABLED=true` no `.env`

---

## 🎯 Próximos Passos

1. **Adicione seus documentos**:
   ```
   POST /v1/rag/default/documents
   {
     "title": "Meu Documento",
     "content": "...",
     "category": "Contratos"
   }
   ```

2. **Integre com o Java API**:
   - Configure `jurisflow.ai.python.url=http://localhost:8090` no `application.yml`
   - Reinicie o Spring Boot

3. **Teste no Frontend**:
   - Acesse `/ia` no JurisFlow
   - Veja o badge "Python online"
   - Teste as chains/agents

4. **Produza**:
   - Mude para Azure OpenAI
   - Use pgvector no lugar do FAISS
   - Configure rate limiting

---

## 📚 Aprender Mais

- **LangChain Docs**: https://python.langchain.com/
- **Groq**: https://console.groq.com/docs
- **RAG Tutorial**: https://python.langchain.com/docs/use_cases/question_answering/
- **Agents**: https://python.langchain.com/docs/modules/agents/

---

**Dúvidas?** Veja o `README.md` completo!
