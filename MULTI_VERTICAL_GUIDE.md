# 🎨 Guia Multi-Vertical - AI Platform

Este guia explica como a plataforma foi refatorada para suportar múltiplos nichos de negócio (verticais).

## 📋 Sumário

- [O que mudou](#o-que-mudou)
- [Estrutura de Verticais](#estrutura-de-verticais)
- [Como Funciona](#como-funciona)
- [Adicionando um Novo Vertical](#adicionando-um-novo-vertical)
- [Migração do Código Antigo](#migração-do-código-antigo)

## O que mudou

### Antes (Monolítico Jurídico)

- Prompts hardcoded no código Python
- Seed RAG fixo no `langchain_store.py`
- Router com regex específica para domínio jurídico
- Nome "Bruna" e "JurisFlow" hardcoded
- Não era possível reutilizar para outros nichos

### Depois (Multi-Vertical Plugável)

- ✅ Prompts em YAML por vertical (`app/verticals/{vertical}/prompts/`)
- ✅ Seed RAG configurável (`app/verticals/{vertical}/seed.yaml`)
- ✅ Router configurável (`app/verticals/{vertical}/router.yaml`)
- ✅ Assistente configurável (nome, role, prompts)
- ✅ Tools de integração configuráveis por vertical
- ✅ Core genérico, reutilizável para N nichos

## Estrutura de Verticais

```
app/verticals/
├── loader.py              # Carregador de configs
├── __init__.py
│
└── legal/                 # Vertical jurídico (template)
    ├── config.yaml        # Configuração principal
    ├── router.yaml        # Padrões de roteamento
    ├── tools.yaml         # Definição de tools
    ├── seed.yaml          # Base de conhecimento inicial
    ├── prompts/           # Prompts por chain/assistente
    │   ├── assistant.yaml
    │   ├── contract_analysis.yaml
    │   ├── document_summary.yaml
    │   ├── jurisprudence_analysis.yaml
    │   ├── case_prediction.yaml
    │   ├── document_generation.yaml
    │   └── legal_research.yaml
    └── README.md          # Documentação do vertical
```

### Arquivos de Configuração

#### `config.yaml`
Define o produto, assistente, chains e URL da API de integração.

```yaml
vertical:
  id: "legal"
  name: "JurisFlow"
  description: "Plataforma de IA para escritórios de advocacia"
  domain: "Jurídico"

assistant:
  name: "Bruna"
  role: "Assistente Jurídica"
  prompt_file: "assistant.yaml"

integration:
  api_url: "${LEGAL_API_URL:http://localhost:8082/api}"
  timeout: 10.0

chains:
  - id: "contract_analysis"
    name: "Análise de Contratos"
    prompt_file: "contract_analysis.yaml"
    enabled: true
  # ... outras chains

agent:
  enabled: true
  max_iterations: 10
  verbose: true
```

#### `router.yaml`
Padrões de detecção de intenção para roteamento inteligente.

```yaml
intents:
  - intent: "buscar_processo"
    keywords: ["processo", "nº", "numero"]
    regex_patterns: ['\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}']
    use_agent: true
    use_rag: false
    explanation: "Detectado número de processo"
  
  - intent: "conversacional"
    default: true
    use_agent: false
    use_rag: true
```

#### `seed.yaml`
Base de conhecimento inicial.

```yaml
documents:
  - title: "Prazos Processuais - CPC"
    category: "Legislação"
    content: |
      ## Prazos Processuais Fundamentais (CPC/2015)
      Contestação (Art. 335): 15 dias úteis...
```

#### `prompts/*.yaml`
Templates de prompts com variáveis.

```yaml
name: "Bruna"
description: "Assistente jurídica conversacional"
temperature: 0.4
max_tokens: 1024

system_prompt: |
  Você é {assistant_name}, assistente do {product_name}.
  
  BASE DE CONHECIMENTO:
  {context}
  
  PERGUNTA:
  {message}
  
  RESPONDA:
```

## Como Funciona

### 1. Carregamento de Configuração

```python
from app.verticals.loader import get_current_vertical

# Carrega o vertical configurado em AI_VERTICAL
vertical = get_current_vertical()

# Acessa configurações
print(vertical.name)              # "JurisFlow"
print(vertical.assistant_name)    # "Bruna"
print(vertical.integration_api_url)  # URL da API
```

### 2. Uso de Prompts

```python
# Carrega prompt do vertical
prompt_config = vertical.load_prompt("assistant")

# Renderiza com variáveis
template = prompt_config["system_prompt"].format(
    assistant_name=vertical.assistant_name,
    product_name=vertical.name,
    context="{context}",
    message="{message}"
)
```

### 3. Seed RAG Dinâmico

```python
# Carrega documentos de seed do vertical
seed_docs = vertical.seed_documents

for doc in seed_docs:
    rag_store.add_document(
        tenant_id,
        DocumentCreate(
            title=doc["title"],
            content=doc["content"],
            category=doc["category"]
        )
    )
```

### 4. Router Configurável

```python
# Carrega padrões de roteamento do vertical
intents = vertical.router_intents

for intent_config in intents:
    keywords = intent_config.get("keywords", [])
    regex_patterns = intent_config.get("regex_patterns", [])
    # ... lógica de detecção
```

## Adicionando um Novo Vertical

### Passo 1: Copiar Template

```bash
cd app/verticals
cp -r legal medical
cd medical
```

### Passo 2: Editar `config.yaml`

```yaml
vertical:
  id: "medical"
  name: "MedAI"
  description: "Plataforma de IA para hospitais"
  domain: "Médico"

assistant:
  name: "Dr. AI"
  role: "Assistente Médico"
  prompt_file: "assistant.yaml"

integration:
  api_url: "${MEDICAL_API_URL:http://localhost:8083/api}"
```

### Passo 3: Customizar Prompts

Edite `prompts/*.yaml` para o domínio médico:

```yaml
# prompts/assistant.yaml
system_prompt: |
  Você é {assistant_name}, assistente médico do {product_name}.
  Ajude profissionais de saúde com diagnósticos, pesquisas...
```

### Passo 4: Configurar Router

Edite `router.yaml` com padrões médicos:

```yaml
intents:
  - intent: "buscar_paciente"
    keywords: ["paciente", "prontuário"]
    use_agent: true
  
  - intent: "diagnostico"
    keywords: ["sintomas", "diagnóstico", "cid"]
    use_agent: false
    use_rag: true
```

### Passo 5: Seed RAG

Edite `seed.yaml` com conhecimento médico:

```yaml
documents:
  - title: "CID-10 - Principais Códigos"
    category: "Classificação"
    content: |
      A00-B99: Doenças infecciosas...
```

### Passo 6: Tools

Edite `tools.yaml` para definir endpoints da API médica:

```yaml
integration_tools:
  - name: "buscar_paciente"
    endpoint: "/v1/pacientes/search"
    method: "GET"
    parameters:
      - name: "cpf"
        type: "string"
        required: true
```

### Passo 7: Configurar `.env`

```bash
AI_VERTICAL=medical
MEDICAL_API_URL=http://localhost:8083/api
```

### Passo 8: Reiniciar Serviço

```bash
uvicorn app.main:app --reload --port 8090
```

## Migração do Código Antigo

### Código que Mudou

| Antes | Depois |
|-------|--------|
| `from app.tools.java_api import java_api_tools` | `from app.tools.integration_api import integration_tools` |
| `JAVA_API_URL = "http://..."` hardcoded | `get_integration_api_url()` dinâmico |
| Prompt hardcoded no código | `vertical.load_prompt("nome")` |
| `DEFAULT_KNOWLEDGE` fixo | `vertical.seed_documents` |
| Router com regex fixas | `vertical.router_intents` |

### Compatibilidade

✅ **Backward compatible**: O alias `java_api_tools` ainda funciona.

✅ **API endpoints**: Não mudaram, apenas internamente agora suportam verticais.

✅ **Banco de dados**: Sem mudanças, RAG continua multi-tenant.

## Benefícios

1. **Reutilização**: Mesma infra para N produtos
2. **Manutenção**: Alterar prompts sem tocar em código
3. **Isolamento**: Cada vertical tem suas configs
4. **Escalabilidade**: Adicionar verticais sem refatoração
5. **Testabilidade**: Testar prompts/routers independentemente

## Próximos Passos

- [ ] Adicionar vertical médico como exemplo
- [ ] Suporte a múltiplos verticais simultâneos (via query param `?vertical=`)
- [ ] UI para editar configs YAML via admin
- [ ] Versionamento de prompts (git-based)
- [ ] A/B testing de prompts por vertical

---

**Documentação**: [app/verticals/legal/README.md](app/verticals/legal/README.md)
