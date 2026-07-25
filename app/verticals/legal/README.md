# Legal Vertical - JurisFlow

Configuração do vertical jurídico para a plataforma de IA.

## Estrutura

```
legal/
├── config.yaml           # Configuração principal do vertical
├── router.yaml          # Padrões de roteamento e detecção de intenção
├── tools.yaml           # Definição de tools do agente
├── seed.yaml            # Base de conhecimento inicial (RAG)
├── prompts/             # Templates de prompts por chain/assistente
│   ├── assistant.yaml
│   ├── contract_analysis.yaml
│   ├── document_summary.yaml
│   ├── jurisprudence_analysis.yaml
│   ├── case_prediction.yaml
│   ├── document_generation.yaml
│   └── legal_research.yaml
└── README.md            # Esta documentação
```

## Configuração

### config.yaml
Define o produto, assistente, chains disponíveis e URL da API de integração.

### router.yaml
Padrões de detecção de intenção para roteamento inteligente:
- Keywords: palavras-chave que indicam cada intenção
- Regex patterns: expressões regulares (ex: número de processo)
- Condições: lógica adicional de decisão
- Estratégia: agent vs chain, uso de RAG

### tools.yaml
Configuração das tools disponíveis para o agente:
- **Integration tools**: chamadas HTTP para a API do backend
- **Local tools**: funções Python locais

### seed.yaml
Base de conhecimento inicial em YAML:
- Documentos categorizados (legislação, jurisprudência, etc)
- Carregados automaticamente no primeiro acesso de cada tenant

### prompts/
Templates de prompts em YAML para cada chain:
- Suporta variáveis dinâmicas: `{variable_name}`
- Configuração de temperature e max_tokens por prompt
- Fácil customização sem modificar código

## Como Adicionar um Novo Vertical

1. Copie a pasta `legal/` como template
2. Renomeie para o ID do seu vertical (ex: `medical/`, `financial/`)
3. Edite `config.yaml`:
   - Altere `vertical.id`, `vertical.name`, `vertical.description`
   - Configure `assistant.name` e `assistant.role`
   - Ajuste `integration.api_url` para a API do seu produto
   - Habilite/desabilite chains conforme necessário
4. Customize `prompts/*.yaml` para seu domínio
5. Ajuste `router.yaml` com padrões do seu domínio
6. Configure `tools.yaml` com endpoints da sua API
7. Popule `seed.yaml` com conhecimento inicial do domínio
8. Configure `AI_VERTICAL=seu_vertical` no `.env`

## Variáveis de Ambiente

```bash
# No .env da aplicação principal
AI_VERTICAL=legal                    # ID do vertical a ser usado
LEGAL_API_URL=http://localhost:8082/api  # URL da API de integração
```

## Exemplo de Uso

Com o vertical configurado, a plataforma carrega automaticamente:

```python
# Endpoint genérico que usa o vertical configurado
POST /v1/chains/run
{
  "chain_id": "contract_analysis",
  "tenant_id": "escritorio_xyz",
  "input": { "contract_text": "..." }
}

# Ou explicitamente para outro vertical
POST /v1/chains/run?vertical=medical
{
  "chain_id": "diagnosis_assistance",
  "tenant_id": "hospital_abc",
  "input": { "symptoms": "..." }
}
```

## Benefícios

- ✅ **Isolamento**: Cada vertical tem suas próprias configurações
- ✅ **Reutilização**: Core da plataforma é genérico
- ✅ **Manutenção**: Alterar prompts sem tocar em código
- ✅ **Escalabilidade**: Adicionar novos verticais sem refatoração
- ✅ **Multi-tenant**: Mesma infra para N produtos
