# 🎯 JurisFlow AI — Portfolio de Engenharia de IA

## Para Apresentação em Entrevistas & Currículo

---

## 📋 Resumo Executivo

**Projeto:** Sistema de Inteligência Artificial Jurídica  
**Stack:** Python + FastAPI + LangChain + RAG + Agents  
**Objetivo:** Demonstrar expertise em Engenharia de IA para aplicações corporativas

### Tecnologias Implementadas
✅ **LangChain** — Framework para aplicações LLM  
✅ **RAG (Retrieval-Augmented Generation)** — FAISS + Embeddings  
✅ **Agents com Tools** — ReAct pattern com 4 ferramentas customizadas  
✅ **Chains** — 3 cadeias de raciocínio especializadas  
✅ **LLM Multi-Provider** — Groq (free), Azure OpenAI, OpenAI  
✅ **Microserviços** — Integração Next.js → Spring Boot → FastAPI  

---

## 🏗️ Arquitetura Implementada

```
Frontend (Next.js)
    ↓
Backend (Spring Boot / Java)
    ↓
AI Service (FastAPI / Python)
    ├─ RAG Engine
    │  ├─ FAISS (Vector Store)
    │  ├─ Sentence Transformers (Embeddings)
    │  └─ RecursiveCharacterTextSplitter
    │
    ├─ LangChain Chains
    │  ├─ Contract Analysis
    │  ├─ Legal Research
    │  └─ Document Generation
    │
    ├─ ReAct Agent
    │  ├─ Tool: calcular_prazo
    │  ├─ Tool: buscar_conhecimento
    │  ├─ Tool: buscar_jurisprudencia
    │  └─ Tool: calcular_honorarios
    │
    └─ LLM Providers
       ├─ Groq (Llama 3.3 70B) — FREE
       ├─ Azure OpenAI (GPT-4o)
       └─ OpenAI (GPT-4o-mini)
```

---

## 🎓 Conhecimentos Demonstrados

### 1. RAG (Retrieval-Augmented Generation)

**Implementação:**
- Vector Store com FAISS (Facebook AI Similarity Search)
- Embeddings locais via `sentence-transformers`
- Chunking inteligente com RecursiveCharacterTextSplitter
- Semantic search com cosine similarity

**Por que RAG?**
- Reduz alucinações do LLM
- Fundamenta respostas em documentos reais
- Escalável (+ documentos = + conhecimento)
- Custo-efetivo (não precisa fine-tuning)

**Código-chave:**
```python
# app/rag/langchain_store.py
vector_store = FAISS.from_documents(documents, embeddings)
results = vector_store.similarity_search_with_score(query, k=5)
```

---

### 2. LangChain Chains

**3 Chains implementadas:**

#### a) Contract Analysis Chain
- Input: Texto do contrato
- Processo: Retrieval → Context Injection → LLM Analysis
- Output: Relatório de riscos com fundamento jurídico

#### b) Legal Research Chain
- Input: Pergunta jurídica
- Processo: RAG Search → Synthesis → Citation
- Output: Resposta fundamentada em documentos

#### c) Document Generation Chain
- Input: Tipo de documento + dados
- Processo: Template Retrieval → LLM Generation
- Output: Minuta formatada

**Padrão:**
```python
chain = (
    RunnablePassthrough.assign(context=retriever)
    | prompt_template
    | llm
    | StrOutputParser()
)
```

---

### 3. Agents com Tools (ReAct Pattern)

**ReAct = Reasoning + Acting**

O agent raciocina sobre qual tool usar e executa ações iterativamente.

**4 Tools customizadas:**

1. **calcular_prazo** — Calcula prazos processuais (corridos/úteis)
2. **buscar_conhecimento** — Busca semântica no RAG
3. **buscar_jurisprudencia** — Busca jurisprudência (simulado, integrável com APIs)
4. **calcular_honorarios** — Calcula honorários OAB

**Exemplo de execução:**

```
User: "Qual prazo para apelar? Sentença em 15/03/2024"

Agent Pensamento: Preciso calcular prazo de apelação
Agent Ação: buscar_conhecimento("prazo apelação")
Agent Observação: "Apelação: 15 dias (art. 1.003 CPC)"

Agent Pensamento: São 15 dias. Preciso calcular data final
Agent Ação: calcular_prazo("15/03/2024", dias_corridos=15)
Agent Observação: "Data final: 30/03/2024"

Agent Resposta: "O prazo é 30/03/2024 (15 dias corridos)"
```

**Código-chave:**
```python
# app/agents/legal_assistant.py
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent, tools, verbose=True)
result = agent_executor.invoke({"input": question})
```

---

### 4. Prompt Engineering

**Técnicas aplicadas:**

✅ **Context Injection** — RAG context no prompt  
✅ **Structured Outputs** — Formatação específica de resposta  
✅ **Few-shot Examples** — Implícitos nos templates  
✅ **Temperature Control** — 0.0 para análise, 0.3 para geração  

**Exemplo:**
```python
template = """Você é um advogado especialista.

## Conhecimento (RAG):
{context}

## Contrato:
{contract}

## Formato de Resposta:
**RESUMO EXECUTIVO:** ...
**CLÁUSULAS DE RISCO:** ...

Resposta:"""
```

---

### 5. Multi-Provider LLM

**Abstração implementada:**
```python
def get_llm(temperature=0.0):
    if provider == "groq":
        return ChatGroq(...)
    elif provider == "azure":
        return AzureChatOpenAI(...)
    elif provider == "openai":
        return ChatOpenAI(...)
```

**Benefícios:**
- Desenvolvimento grátis (Groq)
- Produção paga (Azure)
- Fácil troca de provider

---

## 📊 Métricas & Demonstrabilidade

### Endpoints Implementados

| Categoria | Endpoint | Função |
|-----------|----------|--------|
| RAG | POST /v1/rag/.../search | Busca semântica |
| RAG | POST /v1/rag/.../documents | Adicionar docs |
| Chain | POST /v1/chains/contract-analysis | Análise de contratos |
| Chain | POST /v1/chains/legal-research | Pesquisa jurídica |
| Chain | POST /v1/chains/document-generation | Gerar documentos |
| Agent | POST /v1/agent/ask | Agente com tools |
| Status | GET /v1/status | Status + LLM info |

### Performance
- RAG retrieval: ~100-300ms (FAISS local)
- Chain execution: ~1-3s (depende do LLM)
- Agent com 2 tools: ~3-5s

---

## 🎤 Como Apresentar em Entrevista

### Pergunta: "O que você sabe sobre RAG?"

**Resposta:**
> "Implementei RAG no JurisFlow usando LangChain + FAISS. O fluxo é: documentos jurídicos são chunkados (RecursiveCharacterTextSplitter), convertidos em embeddings (sentence-transformers) e indexados no FAISS. Na query, fazemos similarity search, recuperamos os top-K chunks e injetamos como contexto no prompt do LLM. Isso reduz alucinações e permite o sistema responder com base em conhecimento real do escritório."

### Pergunta: "Já trabalhou com LangChain?"

**Resposta:**
> "Sim, implementei 3 chains e 1 agent no JurisFlow. As chains são para análise de contratos, pesquisa jurídica e geração de documentos. O agent usa ReAct pattern com 4 tools customizadas (calcular prazos, buscar conhecimento, jurisprudência, honorários). Ele raciocina sobre qual tool usar e executa iterativamente até responder a pergunta."

### Pergunta: "Como você integra LLMs?"

**Resposta:**
> "Criei uma abstração que suporta 3 providers: Groq (free, para dev), Azure OpenAI (pago, produção) e OpenAI. Todos via LangChain. No Groq uso Llama 3.3 70B, que é gratuito e rápido. Para produção, migraria para Azure com GPT-4o. A troca é simples, só mudar variável de ambiente."

### Pergunta: "Como você lidaria com escala?"

**Resposta:**
> "Hoje o FAISS é in-memory. Para escala, migraria para pgvector (PostgreSQL com vector search) ou Azure AI Search. Os embeddings locais (sentence-transformers) poderiam ser substituídos por Azure OpenAI ada-002. Para caching de respostas, Redis. E rate limiting no FastAPI."

---

## 📈 Evolução Futura (roadmap)

| Atual | Próximo |
|-------|---------|
| FAISS (local) | **pgvector** ou Azure AI Search |
| Embeddings CPU | **Azure OpenAI Embeddings** |
| Agent simples | **LangGraph multi-agent** |
| Jurisprudência mock | **API STJ/STF oficial** |
| Groq free | **Azure GPT-4o produção** |

---

## 💼 Alinhamento com Vaga

### Requisitos da Vaga vs Implementado

| Requisito | Implementado |
|-----------|--------------|
| RAG | ✅ FAISS + Embeddings + Chunking |
| LLMs | ✅ Multi-provider (Groq, Azure, OpenAI) |
| Agents | ✅ ReAct agent com 4 tools |
| Azure | ✅ Azure OpenAI integrado (config) |
| Python | ✅ FastAPI + LangChain stack |
| Microserviços | ✅ Java API → Python AI Service |

### Palavras-chave no Código (para ATS/recrutadores)
- Retrieval-Augmented Generation
- LangChain chains
- ReAct agents
- Vector embeddings
- Semantic search
- Azure OpenAI
- Prompt engineering
- Cognitive pipelines

---

## 🔗 Links Úteis

- **Repositório:** [GitHub do projeto]
- **Docs Live:** http://localhost:8090/docs
- **README:** Documentação completa
- **EXAMPLES:** Exemplos de uso práticos
- **QUICKSTART:** Setup em 5 minutos

---

## 📝 Resumo em 3 Frases (para currículo)

> Desenvolvido motor de IA jurídica com **RAG (FAISS + embeddings)**, **LangChain chains** para análise de contratos e pesquisa, e **agents ReAct** com 4 tools customizadas. Integra múltiplos LLMs (Groq free, Azure OpenAI, OpenAI) via arquitetura de microserviços **Python FastAPI**. Stack: LangChain, FAISS, sentence-transformers, prompt engineering, semantic search.

---

## 🎯 Pontos-Chave para Destacar

1. **RAG Production-Ready** — Não é só um tutorial, é funcional
2. **Agents com Tools** — Demonstra conhecimento avançado
3. **Prompt Engineering** — Templates estruturados, context injection
4. **Arquitetura Modular** — Fácil evoluir para Azure AI Foundry
5. **Multi-Provider** — Flexibilidade (free → paid)
6. **Documentação Completa** — README, QUICKSTART, EXAMPLES, testes

---

## 🚀 Status

✅ **Pronto para demonstração**  
✅ **Código funcional** (testado)  
✅ **Documentação completa**  
✅ **Evolutível para produção** (Azure migration path clara)

---

**Desenvolvido por:** [Seu Nome]  
**Contato:** [Seu Email/LinkedIn]  
**Tecnologias:** Python, LangChain, FastAPI, RAG, FAISS, Azure OpenAI
