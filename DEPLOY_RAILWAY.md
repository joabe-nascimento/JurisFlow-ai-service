# =================================================================
# GUIA ALTERNATIVO: Deploy JurisFlow AI no Railway.app
# =================================================================
# Railway é uma plataforma moderna que facilita deploy de Python.
# Oferece $5/mês de crédito GRÁTIS (suficiente para hobby projects)
# Deploy em 5 minutos, sem configuração complexa!
#
# Vantagens sobre HostGator:
# ✅ Deploy automático via Git
# ✅ Logs em tempo real
# ✅ SSL/HTTPS automático
# ✅ Sem downtime em reinicializações
# ✅ Suporte oficial a Python/FastAPI
# =================================================================

## PASSO 1: Criar conta no Railway
## ================================

1. Acesse: https://railway.app
2. Clique em "Start a New Project"
3. Faça login com GitHub (recomendado para auto-deploy)

## PASSO 2: Preparar o repositório
## =================================

Certifique-se de que o repositório JurisFlow AI tem os arquivos necessários:

### 2.1. Criar `railway.json` (opcional, mas recomendado)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2.2. Criar `Procfile` (alternativa ao railway.json)

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 2.3. Verificar `requirements.txt`

Certifique-se de que inclui todas as dependências:

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.31.0
python-dotenv>=1.0.1
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
openai>=1.54.0
# ... outras dependências
```

## PASSO 3: Deploy no Railway
## ============================

### Opção A: Deploy via GitHub (recomendado)

1. Faça push do JurisFlow para GitHub (se ainda não fez):
   ```bash
   cd "C:\projetos\projeto-unef\Nova pasta\JurisFlow-ai-service"
   git add railway.json Procfile
   git commit -m "feat: adicionar config para Railway deploy"
   git push origin main
   ```

2. No Railway:
   - Clique em "Deploy from GitHub repo"
   - Autorize o Railway a acessar seus repositórios
   - Selecione o repositório `JurisFlow-ai-service`
   - Clique em "Deploy Now"

3. Railway irá:
   - Detectar que é um projeto Python
   - Instalar dependências do `requirements.txt`
   - Iniciar com o comando do `Procfile`
   - Gerar uma URL temporária (ex: `jurisflow-production.up.railway.app`)

### Opção B: Deploy via Railway CLI

1. Instalar o CLI do Railway:
   ```bash
   npm install -g @railway/cli
   ```

2. Fazer login:
   ```bash
   railway login
   ```

3. Inicializar o projeto:
   ```bash
   cd "C:\projetos\projeto-unef\Nova pasta\JurisFlow-ai-service"
   railway init
   ```

4. Deploy:
   ```bash
   railway up
   ```

## PASSO 4: Configurar variáveis de ambiente
## ===========================================

1. No painel do Railway, vá em:
   - **Settings** > **Variables**

2. Adicione as variáveis do `.env`:

```
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=51hV3vuRzsWgrTjYdeQP0eiwSYRY4sBUYciBZBtutFoBcjmArJQQJ99CGACYeBjFXJ3w3AAABACOG4gIR
AZURE_OPENAI_ENDPOINT=https://uniojuridico-openai.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-5-mini
DATABASE_URL=sqlite:///./jurisflow.db
```

3. Clique em "Add Variable" para cada uma
4. O Railway reiniciará automaticamente o serviço

## PASSO 5: Configurar domínio customizado (opcional)
## ===================================================

### Opção A: Usar domínio Railway (grátis)

Por padrão, o Railway gera: `jurisflow-production.up.railway.app`

Você pode usar esse domínio diretamente!

### Opção B: Usar seu próprio domínio

1. No Railway, vá em: **Settings** > **Networking** > **Custom Domains**
2. Clique em "Add Custom Domain"
3. Digite: `ia.uniojuridico.com.br`
4. Railway mostrará os registros DNS para adicionar:

   **No cPanel do HostGator** (ou gerenciador de DNS):
   - Tipo: `CNAME`
   - Nome: `ia`
   - Valor: `jurisflow-production.up.railway.app`
   - TTL: `3600`

5. Aguarde propagação DNS (5-60 minutos)
6. O Railway gerará SSL/HTTPS automaticamente (Let's Encrypt)

## PASSO 6: Testar o serviço
## ==========================

1. Acesse a URL do Railway:
   ```
   https://jurisflow-production.up.railway.app/health
   ```
   Deve retornar: `{"status":"ok","service":"jurisflow-ai-langchain"}`

2. Teste a documentação:
   ```
   https://jurisflow-production.up.railway.app/docs
   ```

3. Teste um chat:
   ```bash
   curl -X POST https://jurisflow-production.up.railway.app/v1/assistant/bruna/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Olá, bom dia",
       "escritorio_id": "default",
       "history": [],
       "time_context": {"date": "27/07/2026", "time": "10:00", "period": "manhã"}
     }'
   ```

## PASSO 7: Atualizar o Symfony (unio-corp)
## ==========================================

No `.env` do seu projeto Symfony (ou variáveis do HostGator):

```env
LEGAL_AI_ENABLED=true
LEGAL_AI_URL=https://jurisflow-production.up.railway.app
LEGAL_AI_ESCRITORIO_ID=default
```

Ou, se configurou domínio customizado:

```env
LEGAL_AI_URL=https://ia.uniojuridico.com.br
```

Limpe o cache:
```bash
php bin/console cache:clear --env=prod
```

## PASSO 8: Deploy contínuo (CI/CD automático)
## =============================================

Com Railway + GitHub, toda vez que você fizer `git push`, o Railway:
1. Detecta o push
2. Faz rebuild automático
3. Deploy sem downtime
4. Rollback automático se falhar

**Não precisa fazer nada manualmente!** 🎉

## CUSTOS
## =======

**Free Tier do Railway:**
- $5/mês de crédito grátis
- 500 GB-horas de compute
- 100 GB de tráfego

**Para um JurisFlow AI pequeno/médio:**
- ~0.5 vCPU, 512 MB RAM
- ~$3-4/mês (dentro do free tier!)

**Se exceder:** Planos pagos a partir de $5/mês

## MONITORAMENTO
## ==============

No painel do Railway você pode ver:
- ✅ Logs em tempo real
- ✅ Uso de CPU/RAM
- ✅ Requests por segundo
- ✅ Uptime

## COMPARAÇÃO: Railway vs HostGator cPanel
## =========================================

| Característica | Railway | HostGator cPanel |
|----------------|---------|------------------|
| Setup inicial | 5 minutos | 30-60 minutos |
| Auto-deploy | ✅ Sim (Git) | ❌ Manual |
| SSL/HTTPS | ✅ Automático | ⚠️ Compartilhado |
| Logs | ✅ Tempo real | ❌ Arquivo local |
| Restart após crash | ✅ Automático | ❌ Manual |
| Suporte oficial Python | ✅ Sim | ❌ Não (workaround) |
| Custo | $0-5/mês | $0 (já pago) |

## RECOMENDAÇÃO
## =============

🏆 **Use Railway se:**
- Quer facilidade e confiabilidade
- Precisa de deploy automático
- Quer logs e monitoramento
- Pode pagar $0-5/mês extra

🔧 **Use HostGator se:**
- Já paga pelo plano e quer economizar
- Está confortável com workarounds
- Não precisa de uptime crítico
- Tem acesso SSH

=================================================================
