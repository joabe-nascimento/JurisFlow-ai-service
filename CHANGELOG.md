# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - Multi-Vertical Architecture - 2026-07-25

### 🎨 Arquitetura Completamente Refatorada

#### Added
- ✅ **Arquitetura multi-vertical plugável**: Suporte para múltiplos nichos de negócio
- ✅ **Vertical loader**: Carregador dinâmico de configurações por vertical
- ✅ **Prompts em YAML**: Templates de prompts externalizados e configuráveis
- ✅ **Router configurável**: Padrões de detecção de intenção em YAML
- ✅ **Seed RAG dinâmico**: Base de conhecimento inicial por vertical
- ✅ **Tools configuráveis**: Definição de tools em YAML
- ✅ **Assistente configurável**: Nome, role e comportamento por vertical
- ✅ **Integration API genérica**: URL de API configurável por vertical
- ✅ Endpoint `/v1/verticals`: Lista verticais disponíveis
- ✅ Documentação: `MULTI_VERTICAL_GUIDE.md`
- ✅ Template de vertical: `app/verticals/legal/` como referência
- ✅ PyYAML como dependência

#### Changed
- ♻️ **Chains refatoradas**: Agora carregam prompts do vertical
- ♻️ **Router refatorado**: Usa padrões do `router.yaml`
- ♻️ **RAG Store**: Seed carregado dinamicamente do `seed.yaml`
- ♻️ **Orchestrator**: Integra com config do vertical
- ♻️ Renomeado: `java_api.py` → `integration_api.py`
- ♻️ Config: Adicionado `AI_VERTICAL` setting
- ♻️ Status endpoint: Mostra info do vertical ativo
- ♻️ `.env.example`: Adicionado `AI_VERTICAL` e `{VERTICAL}_API_URL`

#### Deprecated
- ⚠️ `java_api_tools`: Use `integration_tools` (alias ainda funciona)

#### Removed
- ❌ Prompts hardcoded removidos do código Python
- ❌ `DEFAULT_KNOWLEDGE` hardcoded removido
- ❌ Regex e keywords hardcoded do router

### 🔧 Estrutura de Arquivos

```
app/
├── verticals/           # NOVO: Configurações por nicho
│   ├── loader.py        # NOVO: Carregador de configs
│   └── legal/           # NOVO: Vertical jurídico (template)
│       ├── config.yaml
│       ├── router.yaml
│       ├── tools.yaml
│       ├── seed.yaml
│       ├── prompts/
│       └── README.md
```

### 📚 Documentação

- `MULTI_VERTICAL_GUIDE.md`: Guia completo de uso
- `app/verticals/legal/README.md`: Documentação do vertical jurídico
- `.env.example`: Atualizado com variáveis de vertical

### 🔄 Backward Compatibility

✅ **100% compatível**: API endpoints não mudaram, apenas internamente agora usam verticals.

### 🚀 Como Usar

```bash
# Configure o vertical no .env
AI_VERTICAL=legal
LEGAL_API_URL=http://localhost:8082/api

# Inicie o serviço
uvicorn app.main:app --reload --port 8090

# Acesse
http://localhost:8090/v1/verticals  # Lista verticais
http://localhost:8090/v1/status     # Info do vertical ativo
```

---

## [1.0.0] - Initial Release

### Added
- FastAPI + LangChain + RAG
- Chains: análise de contratos, pesquisa jurídica, geração de documentos
- Agents: ReAct pattern com tools
- Multi-LLM: OpenRouter, Azure OpenAI, OpenAI
- Fallback automático entre providers
- FAISS Vector Store
- Embeddings locais (sentence-transformers)
- Multi-tenant RAG
- CORS e Rate Limiting
- Dockerfile
- Documentação completa
