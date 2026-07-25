# RAG vs Treinamento — Como a Base de Conhecimento Funciona

Este documento explica o que são os documentos do `seed.yaml`, como o RAG funciona na plataforma e por que isso **não é treinamento de modelo**.

---

## Resumo Rápido

| Conceito | O que é | No JurisFlow |
|----------|---------|--------------|
| **RAG** | Buscar documentos relevantes e injetar no prompt | ✅ Implementado |
| **Seed** | Base de conhecimento inicial por tenant | ✅ `app/verticals/{vertical}/seed.yaml` |
| **Fine-tuning** | Retreinar o modelo com novos dados | ❌ Não implementado |
| **Treinamento** | Alterar pesos do LLM permanentemente | ❌ Não acontece |

**Conclusão:** Os 5 documentos do seed jurídico são **conhecimento consultável**, não **conhecimento aprendido** pelo modelo.

---

## O que é o Seed?

O **seed** é a base de conhecimento inicial carregada automaticamente quando um tenant (escritório) acessa o RAG pela primeira vez.

### Documentos padrão do vertical `legal`

| Título | Categoria | Fonte |
|--------|-----------|-------|
| Prazos Processuais - CPC | Legislação | CPC/2015 |
| LGPD - Lei Geral de Proteção de Dados | Legislação | Lei 13.709/2018 |
| Súmulas STF Mais Relevantes | Jurisprudência | STF |
| CLT - Direitos Trabalhistas Básicos | Legislação | CLT |
| Código Civil - Contratos | Legislação | Lei 10.406/2002 |

### Onde fica configurado

```
app/verticals/legal/seed.yaml
```

Cada vertical pode ter seu próprio seed. Exemplo para um vertical médico: `app/verticals/medical/seed.yaml`.

---

## Como o RAG Funciona (Passo a Passo)

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USUÁRIO PERGUNTA                                            │
│     "Qual o prazo para contestar?"                              │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. EMBEDDING DA PERGUNTA                                       │
│     sentence-transformers converte a pergunta em vetor numérico │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. BUSCA NO FAISS (Vector Store)                               │
│     Compara com chunks dos documentos indexados do tenant       │
│     Retorna os trechos mais similares (top-k)                   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. CONTEXTO ENCONTRADO (exemplo)                                │
│     "Contestação (Art. 335): 15 dias úteis contados da          │
│      audiência de conciliação ou da citação..."                 │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. PROMPT PARA O LLM                                           │
│     System: Você é Bruna, assistente jurídica...                │
│     Context: [trechos do RAG]                                   │
│     User: Qual o prazo para contestar?                          │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. RESPOSTA DO LLM                                             │
│     "O prazo para contestar é de 15 dias úteis, conforme o      │
│      art. 335 do CPC..."                                        │
└─────────────────────────────────────────────────────────────────┘
```

O LLM **não memorizou** o CPC. Ele **leu** o trecho relevante na hora da pergunta.

---

## RAG vs Fine-tuning vs Treinamento

### RAG (o que usamos)

- **Quando:** Em tempo real, a cada pergunta
- **Como:** Indexa documentos → busca similares → injeta no prompt
- **Custo:** Baixo (embeddings locais + FAISS em disco)
- **Atualização:** Adicionar/remover documentos via API
- **Isolamento:** Cada tenant tem sua base separada

### Fine-tuning

- **Quando:** Offline, antes de colocar em produção
- **Como:** Retreina pesos do modelo com dataset curado
- **Custo:** Alto (GPU, dados rotulados, validação)
- **Atualização:** Novo ciclo de treinamento
- **Risco:** Pode degradar comportamento geral do modelo

### Treinamento completo (pre-training)

- **Quando:** Fase de criação do modelo base
- **Como:** Treina do zero com trilhões de tokens
- **Custo:** Muito alto (clusters, meses)
- **Quem faz:** OpenAI, Google, Meta, etc.

---

## Fluxo de Dados no Sistema

### 1. Primeiro acesso do tenant

```http
POST /v1/rag/{escritorio_id}/seed
```

Resposta:

```json
{
  "seeded": 5,
  "total": 5
}
```

O sistema lê `app/verticals/legal/seed.yaml` e indexa os 5 documentos para aquele `escritorio_id`.

### 2. Adicionar documento customizado

```http
POST /v1/rag/{escritorio_id}/documents
Content-Type: application/json

{
  "title": "Contrato Padrão do Escritório",
  "content": "Cláusulas e termos...",
  "category": "Contratos",
  "source": "Interno"
}
```

### 3. Busca semântica

```http
POST /v1/rag/{escritorio_id}/search
Content-Type: application/json

{
  "query": "prazo contestação CPC",
  "limit": 5
}
```

### 4. Uso automático nas chains

Chains como `legal_research`, `jurisprudence_analysis` e o assistente Bruna buscam no RAG automaticamente antes de chamar o LLM.

---

## Multi-tenant: Cada Escritório Tem Sua Base

```
Tenant A (escritorio_abc)
├── Seed padrão (5 docs)
├── Contrato interno A
└── Jurisprudência favorável A

Tenant B (escritorio_xyz)
├── Seed padrão (5 docs)
├── Modelos de petição B
└── Políticas do escritório B
```

Os dados ficam isolados por `escritorio_id`. Um tenant não vê documentos de outro.

---

## O que NÃO acontece

- ❌ O modelo **não aprende** permanentemente com os documentos do seed
- ❌ Não há alteração de pesos do LLM
- ❌ Não é necessário GPU para "treinar"
- ❌ Adicionar documento não exige retreinar nada

---

## Quando Usar Cada Abordagem

| Cenário | Recomendação |
|---------|--------------|
| Base jurídica geral (CPC, CLT, LGPD) | ✅ Seed no `seed.yaml` |
| Documentos do escritório (contratos, modelos) | ✅ RAG via API |
| Tom e estilo da assistente | ✅ Prompts em `prompts/*.yaml` |
| Comportamento especializado profundo | ⚠️ Avaliar fine-tuning (custo alto) |
| Conhecimento que muda frequentemente | ✅ RAG (atualização imediata) |

Para o JurisFlow, a combinação **RAG + prompts configuráveis por vertical** é a abordagem recomendada.

---

## Como Expandir a Base de Conhecimento

### Opção 1: Editar o seed do vertical

Edite `app/verticals/legal/seed.yaml` e adicione documentos:

```yaml
documents:
  - title: "Novo Documento"
    category: "Legislação"
    source: "Lei X"
    content: |
      Conteúdo do documento...
```

Reinicie o serviço Python para novos tenants receberem o seed atualizado.

### Opção 2: API por tenant (recomendado em produção)

Use `POST /v1/rag/{escritorio_id}/documents` para cada escritório adicionar seus próprios documentos sem alterar código.

### Opção 3: Upload em lote (futuro)

Possível evolução: endpoint de upload de PDF/DOCX com chunking automático.

---

## Arquivos Relacionados

| Arquivo | Função |
|---------|--------|
| `app/verticals/legal/seed.yaml` | Documentos iniciais do vertical jurídico |
| `app/rag/langchain_store.py` | Indexação FAISS + embeddings |
| `app/rag/chunker.py` | Divisão de documentos em chunks |
| `app/chains/bruna_assistant.py` | Assistente que usa RAG |
| `app/chains/legal_research.py` | Pesquisa com RAG |
| `MULTI_VERTICAL_GUIDE.md` | Guia da arquitetura multi-vertical |

---

## Perguntas Frequentes

### "Os 5 documentos do seed são treinamento?"

**Não.** São documentos indexados para consulta. O modelo lê na hora da pergunta, não aprende de forma permanente.

### "Preciso retreinar ao adicionar documentos?"

**Não.** Basta adicionar via API ou seed e o FAISS reindexa automaticamente.

### "O seed é igual para todos os escritórios?"

O **conteúdo inicial** vem do mesmo `seed.yaml`, mas cada `escritorio_id` tem **índice isolado**. Depois, cada um pode ter documentos diferentes.

### "Posso ter seeds diferentes por vertical?"

**Sim.** Cada vertical em `app/verticals/{id}/seed.yaml` define sua própria base inicial.

### "Qual a diferença entre seed e prompt?"

- **Seed:** Fatos e conhecimento (leis, súmulas, procedimentos)
- **Prompt:** Instruções de comportamento (tom, formato, regras da Bruna)

---

## Referências

- [MULTI_VERTICAL_GUIDE.md](./MULTI_VERTICAL_GUIDE.md) — Arquitetura multi-nicho
- [app/verticals/legal/README.md](./app/verticals/legal/README.md) — Configuração do vertical jurídico
- [LangChain RAG](https://python.langchain.com/docs/tutorials/rag/) — Documentação oficial
