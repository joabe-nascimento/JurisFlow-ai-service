"""Tools que interagem com a API Java do JurisFlow."""

from typing import Optional, Dict, Any
import httpx
from langchain_core.tools import tool

from app.config import settings


# URL base da API Java (configurável)
JAVA_API_URL = settings.java_api_url if hasattr(settings, 'java_api_url') else "http://localhost:8082/api"


async def call_java_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Helper para chamar API Java."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{JAVA_API_URL}{endpoint}"
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            else:
                return {"error": f"Método {method} não suportado"}
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Erro ao chamar API: {str(e)}"}


@tool
async def buscar_processo(numero_processo: str, escritorio_id: str = "default") -> str:
    """
    Busca informações de um processo no sistema JurisFlow.
    
    Args:
        numero_processo: Número do processo (formato: 0000000-00.0000.0.00.0000)
        escritorio_id: ID do escritório (opcional)
    
    Returns:
        Informações do processo ou mensagem de erro
    
    Exemplo:
        buscar_processo("0001234-56.2024.8.26.0100")
    """
    result = await call_java_api(f"/v1/processos/search?numero={numero_processo}")
    
    if "error" in result:
        return f"Não foi possível buscar o processo: {result['error']}"
    
    if not result.get("data") or not result["data"]:
        return f"Processo {numero_processo} não encontrado no sistema."
    
    processo = result["data"][0] if isinstance(result["data"], list) else result["data"]
    
    info = f"""Processo encontrado: {processo.get('numero', 'N/A')}
Status: {processo.get('status', 'N/A')}
Cliente: {processo.get('cliente', {}).get('nome', 'N/A')}
Tipo: {processo.get('tipo', 'N/A')}
Comarca: {processo.get('comarca', 'N/A')}
"""
    
    if processo.get('valorCausa'):
        info += f"Valor da causa: R$ {processo['valorCausa']:,.2f}\n"
    
    return info


@tool
async def listar_prazos_proximos(dias: int = 7, escritorio_id: str = "default") -> str:
    """
    Lista prazos processuais que vencem nos próximos dias.
    
    Args:
        dias: Número de dias à frente para buscar (padrão: 7)
        escritorio_id: ID do escritório (opcional)
    
    Returns:
        Lista de prazos vencendo ou mensagem se não houver
    
    Exemplo:
        listar_prazos_proximos(15)
    """
    result = await call_java_api(f"/v1/prazos/proximos?dias={dias}")
    
    if "error" in result:
        return f"Não foi possível buscar prazos: {result['error']}"
    
    prazos = result.get("data", [])
    
    if not prazos:
        return f"Não há prazos vencendo nos próximos {dias} dias."
    
    info = f"Prazos vencendo nos próximos {dias} dias:\n\n"
    
    for prazo in prazos[:10]:  # Limita a 10 prazos
        info += f"• {prazo.get('descricao', 'Sem descrição')} - Vence: {prazo.get('dataVencimento', 'N/A')}\n"
        if prazo.get('processo'):
            info += f"  Processo: {prazo['processo'].get('numero', 'N/A')}\n"
    
    if len(prazos) > 10:
        info += f"\n(+{len(prazos) - 10} prazos não exibidos)"
    
    return info


@tool
async def buscar_cliente(nome: str, escritorio_id: str = "default") -> str:
    """
    Busca informações de um cliente no sistema JurisFlow.
    
    Args:
        nome: Nome ou parte do nome do cliente
        escritorio_id: ID do escritório (opcional)
    
    Returns:
        Informações do cliente ou mensagem de erro
    
    Exemplo:
        buscar_cliente("João Silva")
    """
    result = await call_java_api(f"/v1/clientes/search?nome={nome}")
    
    if "error" in result:
        return f"Não foi possível buscar o cliente: {result['error']}"
    
    clientes = result.get("data", [])
    
    if not clientes:
        return f"Cliente '{nome}' não encontrado no sistema."
    
    # Pega o primeiro resultado
    cliente = clientes[0]
    
    info = f"""Cliente encontrado: {cliente.get('nome', 'N/A')}
CPF/CNPJ: {cliente.get('cpfCnpj', 'N/A')}
Email: {cliente.get('email', 'N/A')}
Telefone: {cliente.get('telefone', 'N/A')}
"""
    
    if cliente.get('endereco'):
        info += f"Cidade: {cliente['endereco'].get('cidade', 'N/A')}\n"
    
    # Conta processos
    processos = result.get("processos", [])
    if processos:
        info += f"\nProcessos ativos: {len(processos)}"
    
    return info


@tool
async def verificar_prazo_processo(numero_processo: str) -> str:
    """
    Verifica prazos específicos de um processo.
    
    Args:
        numero_processo: Número do processo
    
    Returns:
        Próximos prazos do processo ou mensagem se não houver
    
    Exemplo:
        verificar_prazo_processo("0001234-56.2024.8.26.0100")
    """
    result = await call_java_api(f"/v1/prazos/processo/{numero_processo}")
    
    if "error" in result:
        return f"Não foi possível verificar prazos: {result['error']}"
    
    prazos = result.get("data", [])
    
    if not prazos:
        return f"Não há prazos cadastrados para o processo {numero_processo}."
    
    info = f"Prazos do processo {numero_processo}:\n\n"
    
    for prazo in prazos:
        status = "⚠️ VENCIDO" if prazo.get("vencido") else "✓ Em dia"
        info += f"• {prazo.get('descricao', 'Sem descrição')} - {prazo.get('dataVencimento', 'N/A')} [{status}]\n"
    
    return info


# Lista de todas as tools para o agent
java_api_tools = [
    buscar_processo,
    listar_prazos_proximos,
    buscar_cliente,
    verificar_prazo_processo,
]
