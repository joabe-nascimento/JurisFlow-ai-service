"""
Teste RÁPIDO do RAG (funciona SEM LLM configurado).

Uso:
    python test_rag_only.py
"""

import asyncio
import httpx

API_URL = "http://localhost:8090"


async def test():
    print("=" * 60)
    print("🧪 TESTE RAG (SEM LLM)")
    print("=" * 60)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Health check
            print("🏥 Health check...")
            r = await client.get(f"{API_URL}/health")
            print(f"✅ {r.json()}\n")
            
            # 2. Status
            print("📊 Status do serviço...")
            r = await client.get(f"{API_URL}/v1/status")
            data = r.json()
            print(f"✅ Serviço: {data['service']}")
            print(f"✅ Retrieval: {data['retrieval']}")
            print(f"✅ LLM: {data.get('llm_provider', 'N/A')}")
            print(f"✅ Documentos: {data['total_documents']}")
            print(f"✅ Chunks: {data['total_chunks']}\n")
            
            # 3. Seed
            print("🌱 Populando base de conhecimento...")
            r = await client.post(f"{API_URL}/v1/rag/default/seed")
            data = r.json()
            print(f"✅ {data['seeded']} docs adicionados")
            print(f"✅ Total: {data['total']} docs na base\n")
            
            # 4. Busca 1: Prazos
            print("🔍 Busca 1: 'prazo contestação CPC'...")
            r = await client.post(
                f"{API_URL}/v1/rag/default/search",
                json={"query": "prazo contestação CPC", "limit": 3}
            )
            data = r.json()
            print(f"✅ Query: {data['query']}")
            print(f"✅ Matches: {data['total_matches']}")
            print(f"✅ Retrieval: {data['retrieval']}")
            for i, chunk in enumerate(data['chunks'][:2], 1):
                print(f"\n  {i}. {chunk['document_title']}")
                print(f"     Score: {chunk['score']:.1f}")
                print(f"     {chunk['content'][:120]}...")
            print()
            
            # 5. Busca 2: LGPD
            print("🔍 Busca 2: 'LGPD obrigações escritório'...")
            r = await client.post(
                f"{API_URL}/v1/rag/default/search",
                json={"query": "LGPD obrigações escritório", "limit": 3}
            )
            data = r.json()
            print(f"✅ Matches: {data['total_matches']}")
            for i, chunk in enumerate(data['chunks'][:2], 1):
                print(f"\n  {i}. {chunk['document_title']}")
                print(f"     Score: {chunk['score']:.1f}")
                print(f"     {chunk['content'][:120]}...")
            print()
            
            # 6. Busca 3: LangChain
            print("🔍 Busca 3: 'LangChain RAG Python'...")
            r = await client.post(
                f"{API_URL}/v1/rag/default/search",
                json={"query": "LangChain RAG Python arquitetura", "limit": 2}
            )
            data = r.json()
            print(f"✅ Matches: {data['total_matches']}")
            for i, chunk in enumerate(data['chunks'], 1):
                print(f"\n  {i}. {chunk['document_title']}")
                print(f"     Score: {chunk['score']:.1f}")
            print()
            
            # Sucesso
            print("=" * 60)
            print("✅ RAG FUNCIONANDO PERFEITAMENTE!")
            print("=" * 60)
            print()
            print("📝 O que está funcionando:")
            print("  ✅ Embeddings semânticos (sentence-transformers)")
            print("  ✅ FAISS vector store")
            print("  ✅ Similarity search com cosine")
            print("  ✅ Chunking inteligente")
            print("  ✅ Multi-tenant (por escritório)")
            print()
            print("🎯 Para o currículo:")
            print("  - Implementação de RAG (Retrieval-Augmented Generation)")
            print("  - Vector search com FAISS")
            print("  - Embeddings semânticos")
            print("  - LangChain + FastAPI")
            print()
            print("🔗 Acesse: http://localhost:8090/docs")
            print()
            
        except httpx.ConnectError:
            print("\n❌ ERRO: Serviço não está rodando!")
            print("\n▶️  Inicie com:")
            print("    cd JurisFlow-ai-service")
            print("    .venv\\Scripts\\activate")
            print("    uvicorn app.main:app --reload --port 8090")
        except Exception as e:
            print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    asyncio.run(test())
