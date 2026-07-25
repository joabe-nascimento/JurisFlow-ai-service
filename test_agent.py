"""
Script de teste rápido para o JurisFlow AI Service.

Uso:
    python test_agent.py
"""

import asyncio
import httpx

API_URL = "http://localhost:8090"


async def test_health():
    """Testa se o serviço está online."""
    print("🏥 Testando health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/health")
        print(f"✅ Health: {response.json()}\n")


async def test_status():
    """Verifica status completo do serviço."""
    print("📊 Verificando status...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/v1/status")
        data = response.json()
        print(f"✅ Serviço: {data['service']}")
        print(f"✅ Versão: {data['version']}")
        print(f"✅ LLM Provider: {data.get('llm_provider', 'N/A')}")
        print(f"✅ LLM Model: {data.get('llm_model', 'N/A')}")
        print(f"✅ LLM Cost: {data.get('llm_cost', 'N/A')}")
        print(f"✅ Retrieval: {data['retrieval']}")
        print(f"✅ Documentos: {data['total_documents']}")
        print(f"✅ Chunks: {data['total_chunks']}\n")


async def test_seed():
    """Popula base de conhecimento inicial."""
    print("🌱 Populando base de conhecimento...")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/v1/rag/default/seed")
        data = response.json()
        print(f"✅ Seed: {data['seeded']} documentos adicionados")
        print(f"✅ Total: {data['total']} documentos na base\n")


async def test_search():
    """Testa busca semântica."""
    print("🔍 Testando busca semântica (RAG)...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/v1/rag/default/search",
            json={"query": "prazo contestação CPC", "limit": 3}
        )
        data = response.json()
        print(f"✅ Query: {data['query']}")
        print(f"✅ Matches: {data['total_matches']}")
        print(f"✅ Retrieval: {data['retrieval']}")
        for i, chunk in enumerate(data['chunks'], 1):
            print(f"\n  {i}. {chunk['document_title']} (score: {chunk['score']:.1f})")
            print(f"     {chunk['content'][:150]}...")
        print()


async def test_agent_prazo():
    """Testa agent calculando prazo."""
    print("🤖 Testando Agent: Calcular Prazo...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_URL}/v1/agent/ask",
            json={
                "question": "Qual o prazo final para apelar se a sentença foi publicada em 15/03/2024? São 15 dias úteis.",
                "escritorio_id": "default",
                "mode": "full"
            }
        )
        data = response.json()
        
        if data.get("error"):
            print(f"❌ Erro: {data['answer']}\n")
            return
        
        print(f"✅ Resposta: {data['answer'][:200]}...")
        print(f"✅ Iterações: {data.get('iterations', 0)}")
        
        if data.get('steps'):
            print(f"\n📝 Passos executados:")
            for i, step in enumerate(data['steps'], 1):
                print(f"  {i}. Tool: {step['tool']}")
                print(f"     Input: {step['input']}")
                print(f"     Output: {step['output'][:100]}...")
        print()


async def test_agent_honorarios():
    """Testa agent calculando honorários."""
    print("🤖 Testando Agent: Calcular Honorários...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_URL}/v1/agent/ask",
            json={
                "question": "Calcule honorários para uma ação trabalhista de R$ 85.000 com 20% de êxito",
                "escritorio_id": "default",
                "mode": "answer_only"
            }
        )
        data = response.json()
        
        if data.get("error"):
            print(f"❌ Erro: {data['answer']}\n")
            return
        
        print(f"✅ Resposta:\n{data['answer']}\n")


async def test_chain_research():
    """Testa chain de pesquisa jurídica."""
    print("⛓️  Testando Chain: Legal Research...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_URL}/v1/chains/legal-research",
            json={
                "question": "Quais são os prazos do CPC para recursos?",
                "escritorio_id": "default"
            }
        )
        data = response.json()
        print(f"✅ Pergunta: {data['question']}")
        print(f"✅ Resposta:\n{data['answer'][:300]}...\n")


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🚀 JURISFLOW AI SERVICE - TESTES")
    print("=" * 60)
    print()
    
    try:
        await test_health()
        await test_status()
        await test_seed()
        await test_search()
        await test_agent_prazo()
        await test_agent_honorarios()
        await test_chain_research()
        
        print("=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        print()
        print("📚 Veja mais exemplos em: EXAMPLES.md")
        print("📖 Documentação completa: README.md")
        print("🔗 API Docs: http://localhost:8090/docs")
        
    except httpx.ConnectError:
        print("\n❌ ERRO: Serviço não está rodando!")
        print("Inicie o serviço com: uvicorn app.main:app --reload --port 8090")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")


if __name__ == "__main__":
    asyncio.run(main())
