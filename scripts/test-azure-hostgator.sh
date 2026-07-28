#!/bin/bash
set -eu
cd /home2/joabef36/jurisflow-ai
source .venv/bin/activate

KEY=$(grep '^AZURE_OPENAI_KEY=' .env | cut -d= -f2-)
ENDPOINT=$(grep '^AZURE_OPENAI_ENDPOINT=' .env | cut -d= -f2- | tr -d '\r')
DEPLOY=$(grep '^AZURE_DEPLOYMENT_NAME=' .env | cut -d= -f2- | tr -d '\r')
URL="${ENDPOINT%/}/openai/deployments/${DEPLOY}/chat/completions?api-version=2024-12-01-preview"

echo "URL=$URL"
echo "Testing key 1 via curl..."
curl -sS --http1.1 -o /tmp/azure_resp.json -w "HTTP %{http_code}\n" \
  -X POST "$URL" \
  -H "api-key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Oi"}],"max_tokens":50}'

head -c 500 /tmp/azure_resp.json; echo

KEY2="ijk6jltsyfk7xlG113pr3RIpc5kiCStcrzaDgBnyJKPMe5ixb9T9JQQJ99CGACYeBjFXJ3w3AAABACOGFLZA"
echo "Testing key 2 via curl..."
curl -sS -o /tmp/azure_resp2.json -w "HTTP %{http_code}\n" \
  -X POST "$URL" \
  -H "api-key: $KEY2" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Oi"}],"max_tokens":50}'

head -c 500 /tmp/azure_resp2.json; echo
