import httpx

payload = {
    "message": "Ola, bom dia",
    "escritorio_id": "default",
    "use_rag": False,
    "history": [],
    "time_context": {"date": "27/07/2026", "time": "11:30", "period": "manhã"},
}
r = httpx.post("http://127.0.0.1:8091/v1/assistant/bruna/chat", json=payload, timeout=90)
print("status", r.status_code)
print(r.text[:3000])
