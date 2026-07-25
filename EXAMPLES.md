# 📚 Exemplos Práticos — JurisFlow AI

## 1️⃣ RAG Básico

### Adicionar documento
```bash
curl -X POST http://localhost:8090/v1/rag/default/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lei 8.906/94 - Estatuto da OAB",
    "content": "Art. 22. A prestação de serviço profissional assegura aos inscritos na OAB o direito aos honorários convencionados, aos fixados por arbitramento judicial e aos de sucumbência.",
    "category": "Honorários",
    "source": "Lei 8.906/94"
  }'
```

### Buscar
```bash
curl -X POST http://localhost:8090/v1/rag/default/search \
  -H "Content-Type: application/json" \
  -d '{"query": "honorários advocatícios", "limit": 3}'
```

---

## 2️⃣ Chain: Análise de Contratos

### Exemplo completo
```bash
curl -X POST http://localhost:8090/v1/chains/contract-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n\nCLÁUSULA 1 - DO OBJETO\nA CONTRATADA prestará serviços de desenvolvimento de software.\n\nCLÁUSULA 5 - DA LIMITAÇÃO DE RESPONSABILIDADE\nA CONTRATADA não se responsabiliza por quaisquer danos diretos, indiretos, lucros cessantes ou danos morais.\n\nCLÁUSULA 8 - DA RESCISÃO\nEste contrato poderá ser rescindido pela CONTRATANTE a qualquer momento, sem necessidade de aviso prévio ou pagamento de indenização.\n\nCLÁUSULA 12 - DO FORO\nFica eleito o foro da comarca de São Paulo/SP para dirimir quaisquer controvérsias.",
    "escritorio_id": "default"
  }'
```

### Resposta esperada
```
**RESUMO EXECUTIVO:**
Contrato apresenta 3 cláusulas de ALTO risco que podem prejudicar significativamente o CONTRATADO.

**CLÁUSULAS DE RISCO IDENTIFICADAS:**

1. Limitação de Responsabilidade - Risco: ALTO
   - Texto: "não se responsabiliza por quaisquer danos diretos, indiretos..."
   - Problema: Exclusão total de responsabilidade é abusiva
   - Sugestão: Limitar apenas danos indiretos, mantendo responsabilidade por danos diretos
   - Fundamento: Art. 51, I CDC - cláusula que exonere responsabilidade é nula

2. Rescisão Imotivada - Risco: ALTO
   - Texto: "poderá ser rescindido...sem aviso prévio ou indenização"
   - Problema: Permite rescisão unilateral sem proteção ao contratado
   - Sugestão: Incluir aviso prévio de 30 dias ou pagamento proporcional
   - Fundamento: Boa-fé contratual (CC art. 422)

3. Foro Exclusivo - Risco: MÉDIO
   - Texto: "eleito o foro da comarca de São Paulo/SP"
   - Problema: Pode dificultar acesso à justiça se contratado for de outra região
   - Sugestão: Foro do domicílio do réu ou local da prestação do serviço
```

---

## 3️⃣ Chain: Pesquisa Jurídica

### Pergunta sobre prazos
```bash
curl -X POST http://localhost:8090/v1/chains/legal-research \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais são os prazos para recursos no CPC?",
    "escritorio_id": "default"
  }'
```

### Pergunta sobre LGPD
```bash
curl -X POST http://localhost:8090/v1/chains/legal-research \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais as obrigações de um escritório de advocacia segundo a LGPD?",
    "escritorio_id": "default"
  }'
```

---

## 4️⃣ Chain: Geração de Documentos

### Gerar Petição Inicial
```bash
curl -X POST http://localhost:8090/v1/chains/document-generation \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "Petição Inicial - Ação de Cobrança",
    "data": "Autor: JOÃO DA SILVA, CPF 123.456.789-00, residente na Rua A, 100\nRéu: EMPRESA XYZ LTDA, CNPJ 12.345.678/0001-99\nValor: R$ 50.000,00\nMotivo: Prestação de serviços não pagos, conforme contrato de 01/01/2024",
    "escritorio_id": "default"
  }'
```

### Gerar Procuração
```bash
curl -X POST http://localhost:8090/v1/chains/document-generation \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "Procuração Ad Judicia",
    "data": "Outorgante: MARIA SANTOS, CPF 987.654.321-00\nOutorgado: Dr. Pedro Oliveira, OAB/SP 123.456\nPoderes: Gerais para o foro (cláusula ad judicia)",
    "escritorio_id": "default"
  }'
```

---

## 5️⃣ Agent: Exemplos de Perguntas

### Calcular Prazo
```bash
curl -X POST http://localhost:8090/v1/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual o prazo final para apelar se a sentença foi publicada em 15/03/2024? Preciso de 15 dias úteis.",
    "mode": "full"
  }'
```

**O agent vai:**
1. Identificar que precisa calcular prazo
2. Usar a tool `calcular_prazo`
3. Retornar data final + explicação

### Buscar + Calcular
```bash
curl -X POST http://localhost:8090/v1/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Preciso saber o prazo para contestação segundo o CPC. A citação foi em 10/02/2024. Calcule a data final.",
    "mode": "full"
  }'
```

**O agent vai:**
1. Usar `buscar_conhecimento` para encontrar "prazo contestação CPC"
2. Identificar que são 15 dias úteis (art. 335 CPC)
3. Usar `calcular_prazo` com data 10/02/2024 e 15 dias úteis
4. Retornar resposta completa

### Calcular Honorários
```bash
curl -X POST http://localhost:8090/v1/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Calcule os honorários para uma ação trabalhista de R$ 120.000,00 com 20% de êxito",
    "mode": "full"
  }'
```

### Pesquisa Complexa
```bash
curl -X POST http://localhost:8090/v1/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Busque jurisprudência do STJ sobre dano moral e depois me diga quanto deveria cobrar de honorários para uma ação de R$ 80.000",
    "mode": "full"
  }'
```

**O agent vai:**
1. Usar `buscar_jurisprudencia("dano moral", "STJ")`
2. Analisar o resultado
3. Usar `calcular_honorarios(80000, "cível")`
4. Combinar as informações na resposta

---

## 6️⃣ Modo "answer_only" vs "full"

### Full (mostra raciocínio)
```json
{
  "question": "Calcule prazo de 15 dias úteis a partir de 01/03/2024",
  "mode": "full"
}
```

**Resposta:**
```json
{
  "answer": "O prazo final é 22/03/2024...",
  "steps": [
    {
      "tool": "calcular_prazo",
      "input": {"data_inicial": "01/03/2024", "dias_uteis": 15},
      "output": "Data inicial: 01/03/2024\nPrazo: 15 dias úteis..."
    }
  ],
  "iterations": 1
}
```

### Answer Only (só resposta)
```json
{
  "question": "Calcule prazo de 15 dias úteis a partir de 01/03/2024",
  "mode": "answer_only"
}
```

**Resposta:**
```json
{
  "answer": "O prazo final é 22/03/2024..."
}
```

---

## 7️⃣ Fluxo Completo: Análise de Caso

```bash
# 1. Popular base com documentos relevantes
curl -X POST http://localhost:8090/v1/rag/default/seed

# 2. Adicionar jurisprudência específica
curl -X POST http://localhost:8090/v1/rag/default/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Precedente STJ - Dano Moral Coletivo",
    "content": "REsp 1.452.360/RS - Em demandas coletivas, o valor do dano moral deve considerar o impacto social e a capacidade inibitória da condenação.",
    "category": "Jurisprudência"
  }'

# 3. Usar o agent para análise completa
curl -X POST http://localhost:8090/v1/agent/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tenho uma ação coletiva de dano moral contra uma empresa. O valor da causa é R$ 500.000. Busque informações sobre dano moral coletivo na base e calcule meus honorários com 25% de êxito.",
    "mode": "full"
  }'
```

---

## 8️⃣ Python SDK

### Uso programático
```python
import httpx

API_URL = "http://localhost:8090"

async def ask_agent(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/v1/agent/ask",
            json={
                "question": question,
                "escritorio_id": "default",
                "mode": "full"
            }
        )
        return response.json()

# Uso
result = await ask_agent("Qual prazo para contestação?")
print(result["answer"])
```

---

## 9️⃣ Integração com Java API

```java
// Em PythonAIService.java

public AgentResponse askAgent(String question, String escritorioId) {
    AgentRequest request = new AgentRequest();
    request.setQuestion(question);
    request.setEscritorioId(escritorioId);
    request.setMode("full");
    
    return restTemplate.postForObject(
        pythonUrl + "/v1/agent/ask",
        request,
        AgentResponse.class
    );
}
```

---

## 🔟 Debug & Observability

### Ver logs do agent (verbose mode)
No terminal onde o server está rodando, com `AGENT_VERBOSE=true`:

```
> Entering new AgentExecutor chain...
Pensamento: Preciso calcular o prazo para contestação
Ação: buscar_conhecimento
Entrada da Ação: {"query": "prazo contestação CPC", "escritorio_id": "default"}
Observação: Encontrados 2 resultados para 'prazo contestação CPC':
1. Código de Processo Civil - Prazos (score: 85.3)
   Contestação: 15 dias úteis (art. 335 CPC)...

Pensamento: Agora sei que são 15 dias úteis. Preciso calcular a data final
Ação: calcular_prazo
Entrada da Ação: {"data_inicial": "10/02/2024", "dias_uteis": 15}
Observação: Data inicial: 10/02/2024
Prazo: 15 dias úteis
Data final: 01/03/2024

Pensamento: Agora sei a resposta final
Resposta Final: O prazo para contestação é de 15 dias úteis...
```

---

## 💡 Dicas de Uso

1. **Seed sempre primeiro**: `POST /v1/rag/default/seed`
2. **Agent é melhor para múltiplas operações**: Chains são boas para uma tarefa específica
3. **Use mode="full"** em desenvolvimento para ver o raciocínio
4. **Adicione seus documentos**: Quanto mais contexto, melhor a resposta
5. **Teste no Swagger**: http://localhost:8090/docs tem interface interativa

---

## 🎯 Casos de Uso por Funcionalidade

| Preciso... | Use... |
|------------|--------|
| Analisar um contrato | Chain: `/v1/chains/contract-analysis` |
| Responder pergunta jurídica | Chain: `/v1/chains/legal-research` |
| Gerar documento | Chain: `/v1/chains/document-generation` |
| Calcular prazo | Agent: `/v1/agent/ask` |
| Calcular honorários | Agent: `/v1/agent/ask` |
| Buscar jurisprudência | Agent: `/v1/agent/ask` |
| Tarefa complexa (múltiplas operações) | Agent: `/v1/agent/ask` |
| Só buscar na base | RAG: `/v1/rag/.../search` |

---

**Explore mais na documentação Swagger**: http://localhost:8090/docs
