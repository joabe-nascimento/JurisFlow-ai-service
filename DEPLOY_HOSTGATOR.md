# =================================================================
# GUIA: Deploy JurisFlow AI no HostGator cPanel (Shared Hosting)
# =================================================================
# Este é um workaround não-oficial. O HostGator compartilhado não
# suporta oficialmente Python persistente, mas funciona via proxy.
#
# Referências:
# - https://dev.to/cmanish049/how-to-deploy-fastapi-on-shared-hosting-cpanel-7ch
# - https://lucidgen.com/en/how-to-deploy-fastapi-on-cpanel/
# =================================================================

## PASSO 1: Fazer upload dos arquivos
## ====================================

1. Acesse o cPanel do HostGator
2. Vá em: Arquivos > Gerenciador de Arquivos
3. Navegue até o diretório desejado (ex: /home/usuario/jurisflow-ai)
4. Faça upload de todos os arquivos do JurisFlow AI (app/, requirements.txt, etc.)

Estrutura esperada:
```
/home/usuario/jurisflow-ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── chains/
│   ├── agents/
│   └── ...
├── requirements.txt
└── .env
```

## PASSO 2: Criar Python App no cPanel
## ====================================

1. Vá em: Software > Setup Python App
2. Clique em "Create Application"
3. Configure:
   - Python version: 3.11 ou 3.12
   - Application root: /home/usuario/jurisflow-ai
   - Application URL: ia.uniojuridico.com.br (ou subdomínio desejado)
   - Application startup file: [deixe em branco ou main.py]
   - Application Entry point: [deixe em branco ou app]
4. Clique em "CREATE"

⚠️ **IMPORTANTE**: O cPanel criará um ambiente virtual Python. 
COPIE o comando de ativação que aparece (ex: `source /home/usuario/virtualenv/ia_uniojuridico_com_br/3.11/bin/activate`)

5. Clique em "STOP APP" (não vamos usar o Passenger WSGI)

## PASSO 3: Instalar dependências via Terminal SSH
## ================================================

1. Acesse: Advanced > Terminal (ou use SSH externo)
2. Execute os comandos:

```bash
# Ativar o ambiente virtual (use o comando que você copiou no passo 2)
source /home/usuario/virtualenv/ia_uniojuridico_com_br/3.11/bin/activate

# Navegar para o diretório do app
cd /home/usuario/jurisflow-ai

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Instalar uvicorn (se não estiver no requirements.txt)
pip install uvicorn[standard]
```

## PASSO 4: Configurar variáveis de ambiente (.env)
## =================================================

Edite o arquivo `.env` no diretório `/home/usuario/jurisflow-ai/`:

```env
# LLM — Azure OpenAI (produção / Unio Jurídico)
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=51hV3vuRzsWgrTjYdeQP0eiwSYRY4sBUYciBZBtutFoBcjmArJQQJ99CGACYeBjFXJ3w3AAABACOG4gIR
AZURE_OPENAI_ENDPOINT=https://uniojuridico-openai.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-5-mini

# PostgreSQL local (ou remoto, se aplicável)
DATABASE_URL=sqlite:///./jurisflow.db

# Porta interna (não exposta publicamente)
PORT=8090
```

## PASSO 5: Iniciar o serviço em background
## ==========================================

No Terminal SSH, execute:

```bash
# Certificar-se de estar no diretório correto com venv ativado
source /home/usuario/virtualenv/ia_uniojuridico_com_br/3.11/bin/activate
cd /home/usuario/jurisflow-ai

# Iniciar uvicorn em background (nohup = não desliga ao fechar terminal)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8090 > jurisflow.log 2>&1 &

# Verificar se está rodando
ps aux | grep uvicorn

# Ver logs em tempo real (Ctrl+C para sair)
tail -f jurisflow.log
```

✅ O serviço agora está rodando em `http://127.0.0.1:8090` internamente.

## PASSO 6: Configurar Reverse Proxy (.htaccess)
## ===============================================

1. No diretório raiz do seu domínio/subdomínio (ex: `/home/usuario/public_html/ia`), 
   crie ou edite o arquivo `.htaccess`:

```apache
RewriteEngine On

# Forçar HTTPS (recomendado)
RewriteCond %{HTTPS} !=on
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]

# Reverse Proxy para o JurisFlow AI local
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ http://127.0.0.1:8090/$1 [P,L]
```

**Explicação:**
- Linha 1-2: Habilita reescrita de URLs
- Linha 4-6: Força HTTPS (importante para produção)
- Linha 8-11: Redireciona todo o tráfego para o uvicorn na porta 8090

## PASSO 7: Testar o serviço
## ==========================

1. Acesse no navegador: https://ia.uniojuridico.com.br/health
   - Deve retornar: `{"status":"ok","service":"jurisflow-ai-langchain"}`

2. Teste a documentação: https://ia.uniojuridico.com.br/docs
   - Deve abrir a interface Swagger UI

3. Teste um chat: 
   ```bash
   curl -X POST https://ia.uniojuridico.com.br/v1/assistant/bruna/chat \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Olá, bom dia",
       "escritorio_id": "default",
       "history": [],
       "time_context": {"date": "27/07/2026", "time": "10:00", "period": "manhã"}
     }'
   ```

## PASSO 8: Auto-restart (watchdog via cron)
## ==========================================

O `scripts/setup-hostgator.sh` instala automaticamente um cron que roda a cada 5
minutos com `flock` (evita reinícios concorrentes). O watchdog verifica
`/health` na porta **8091** e reinicia com `setsid` (desacoplado da sessão SSH).

Comando instalado no cron:
```bash
*/5 * * * * flock -n /home2/joabef36/jurisflow-ai/.watchdog.lock /home2/joabef36/jurisflow-ai/scripts/watchdog-hostgator.sh >/dev/null 2>&1
```

Comandos manuais úteis:
```bash
bash scripts/start-hostgator.sh   # inicia desacoplado (setsid)
bash scripts/stop-hostgator.sh    # para o serviço
bash scripts/watchdog-hostgator.sh  # força verificação imediata
tail -f watchdog.log              # log do watchdog
```

> **Nota:** `systemd --user` não funciona no HostGator compartilhado. O cron +
> `setsid` é a solução persistente recomendada.

## PASSO 9: Atualizar o Symfony (.env no HostGator)
## ==================================================

No seu projeto Symfony (unio-corp), configure o `.env` ou variáveis de ambiente:

```env
LEGAL_AI_ENABLED=true
LEGAL_AI_URL=https://ia.uniojuridico.com.br
LEGAL_AI_ESCRITORIO_ID=default
```

Limpe o cache:
```bash
php bin/console cache:clear --env=prod
```

## PASSO 10: Verificar se tudo funciona
## =====================================

Acesse a plataforma Unio Jurídico e teste a Bruna. Ela deve responder normalmente!

=================================================================
TROUBLESHOOTING
=================================================================

## Problema: "502 Bad Gateway"
**Causa:** O uvicorn não está rodando ou a porta está errada.
**Solução:** 
```bash
ps aux | grep uvicorn
tail -f /home/usuario/jurisflow-ai/jurisflow.log
```

## Problema: "Cannot find module 'app'"
**Causa:** Ambiente virtual não ativado ou dependências não instaladas.
**Solução:** 
```bash
source /home/usuario/virtualenv/ia_uniojuridico_com_br/3.11/bin/activate
pip install -r requirements.txt
```

## Problema: "Port 8090 already in use"
**Causa:** Outro processo está usando a porta.
**Solução:** 
```bash
# Encontrar o processo
lsof -i :8090
# Matar o processo (substitua PID)
kill -9 <PID>
# Ou use outra porta (8091, 8092, etc.) e ajuste o .htaccess
```

## Problema: Bruna não responde em produção
**Causa:** Variáveis de ambiente não configuradas ou cache não limpo.
**Solução:** 
- Verificar `.env` do Symfony
- Rodar `php bin/console cache:clear --env=prod`
- Testar diretamente: `curl https://ia.uniojuridico.com.br/health`

=================================================================
