"""
Tools que interagem com a API interna do backend (Unio Jurídico).

Cada vertical pode ter sua própria API de backend configurada em
app/verticals/{vertical}/config.yaml na seção 'integration'. A URL aponta para
um endpoint INTERNO (servidor-a-servidor), autenticado por segredo compartilhado
(header X-Internal-Secret) — não é a API pública usada por integrações de terceiros.
"""

from functools import partial
from typing import Optional, Dict, Any, List
from urllib.parse import quote
import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class _BuscarProcessoArgs(BaseModel):
    numero_processo: str = Field(description="Número do processo (formato: 0000000-00.0000.0.00.0000)")


class _ListarPrazosArgs(BaseModel):
    dias: int = Field(default=7, description="Número de dias à frente para buscar (padrão: 7)")


class _BuscarClienteArgs(BaseModel):
    nome: str = Field(description="Nome ou parte do nome do cliente")


class _VerificarPrazoProcessoArgs(BaseModel):
    numero_processo: str = Field(description="Número do processo")


def get_integration_api_url() -> str:
    """Retorna a URL da API de integração do vertical atual."""
    from app.verticals.loader import get_current_vertical
    return get_current_vertical().integration_api_url


def get_integration_timeout() -> float:
    """Retorna o timeout configurado para a API de integração."""
    from app.verticals.loader import get_current_vertical
    return get_current_vertical().integration_timeout


def get_integration_secret() -> str:
    """Segredo compartilhado enviado no header X-Internal-Secret."""
    from app.config import settings
    return settings.legal_api_secret


async def call_integration_api(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    escritorio_id: str = "default",
) -> Dict[str, Any]:
    """
    Helper para chamar a API interna do backend, sempre escopada por escritorio_id.

    A URL base é carregada dinamicamente do vertical configurado.
    """
    try:
        api_url = get_integration_api_url()
        timeout = get_integration_timeout()
        secret = get_integration_secret()

        headers = {"X-Internal-Secret": secret} if secret else {}

        separator = "&" if "?" in endpoint else "?"
        url = f"{api_url}{endpoint}{separator}escritorio_id={quote(escritorio_id)}"
        if secret:
            # Alguns hosts (ex.: LiteSpeed/CGI na HostGator) descartam headers
            # HTTP customizados antes de chegar ao PHP — mandamos o segredo
            # também via query string como alternativa confiável.
            url = f"{url}&internal_secret={quote(secret)}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers)
            else:
                return {"error": f"Método {method} não suportado"}

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Erro ao chamar API de integração: {str(e)}"}


async def _buscar_processo(numero_processo: str, escritorio_id: str) -> str:
    """
    Busca informações de um processo no sistema.

    Args:
        numero_processo: Número do processo (formato: 0000000-00.0000.0.00.0000)

    Returns:
        Informações do processo ou mensagem de erro

    Exemplo:
        buscar_processo("0001234-56.2024.8.26.0100")
    """
    result = await call_integration_api(
        f"/processos?numero={quote(numero_processo)}",
        escritorio_id=escritorio_id,
    )

    if "error" in result:
        return f"Não foi possível buscar o processo: {result['error']}"

    if not result.get("data") or not result["data"]:
        return f"Processo {numero_processo} não encontrado no sistema."

    processo = result["data"][0] if isinstance(result["data"], list) else result["data"]

    info = f"""Processo encontrado: {processo.get('numero', 'N/A')}
Status: {processo.get('status', 'N/A')}
Cliente: {processo.get('cliente', {}).get('nome', 'N/A')}
Área: {processo.get('area', 'N/A')}
Tribunal: {processo.get('tribunal', 'N/A')}
"""

    if processo.get('valorCausa'):
        try:
            valor = float(str(processo['valorCausa']).replace(',', '.'))
            info += f"Valor da causa: R$ {valor:,.2f}\n"
        except (TypeError, ValueError):
            info += f"Valor da causa: {processo['valorCausa']}\n"

    return info


async def _listar_prazos_proximos(escritorio_id: str, dias: int = 7) -> str:
    """
    Lista prazos processuais que vencem nos próximos dias.

    Args:
        dias: Número de dias à frente para buscar (padrão: 7)

    Returns:
        Lista de prazos vencendo ou mensagem se não houver

    Exemplo:
        listar_prazos_proximos(15)
    """
    result = await call_integration_api(f"/prazos?dias={dias}", escritorio_id=escritorio_id)

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


async def _buscar_cliente(nome: str, escritorio_id: str) -> str:
    """
    Busca informações de um cliente no sistema.

    Args:
        nome: Nome ou parte do nome do cliente

    Returns:
        Informações do cliente ou mensagem de erro

    Exemplo:
        buscar_cliente("João Silva")
    """
    result = await call_integration_api(f"/clientes?nome={quote(nome)}", escritorio_id=escritorio_id)

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

    return info


async def _verificar_prazo_processo(numero_processo: str, escritorio_id: str) -> str:
    """
    Verifica prazos específicos de um processo.

    Args:
        numero_processo: Número do processo

    Returns:
        Próximos prazos do processo ou mensagem se não houver

    Exemplo:
        verificar_prazo_processo("0001234-56.2024.8.26.0100")
    """
    result = await call_integration_api(
        f"/prazos/processo/{quote(numero_processo, safe='')}",
        escritorio_id=escritorio_id,
    )

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


def get_integration_tools(escritorio_id: str) -> List[StructuredTool]:
    """
    Cria as tools de integração já *escopadas* para um escritorio_id fixo.

    Importante: o escritorio_id NÃO fica exposto como parâmetro que o LLM
    possa escolher/alucinar — é fixado pelo backend (vindo da sessão/JWT do
    usuário autenticado), evitando que uma tool acesse dados de outro
    escritório por engano ou por injeção de prompt.
    """
    return [
        StructuredTool.from_function(
            coroutine=partial(_buscar_processo, escritorio_id=escritorio_id),
            name="buscar_processo",
            description=(
                "Busca informações de um processo no sistema pelo número "
                "(formato: 0000000-00.0000.0.00.0000). "
                "Exemplo: buscar_processo(numero_processo='0001234-56.2024.8.26.0100')"
            ),
            args_schema=_BuscarProcessoArgs,
        ),
        StructuredTool.from_function(
            coroutine=partial(_listar_prazos_proximos, escritorio_id=escritorio_id),
            name="listar_prazos_proximos",
            description=(
                "Lista prazos processuais que vencem nos próximos N dias (padrão 7). "
                "Exemplo: listar_prazos_proximos(dias=15)"
            ),
            args_schema=_ListarPrazosArgs,
        ),
        StructuredTool.from_function(
            coroutine=partial(_buscar_cliente, escritorio_id=escritorio_id),
            name="buscar_cliente",
            description=(
                "Busca informações de um cliente do escritório pelo nome. "
                "Exemplo: buscar_cliente(nome='João Silva')"
            ),
            args_schema=_BuscarClienteArgs,
        ),
        StructuredTool.from_function(
            coroutine=partial(_verificar_prazo_processo, escritorio_id=escritorio_id),
            name="verificar_prazo_processo",
            description=(
                "Verifica os prazos cadastrados para um processo específico pelo número. "
                "Exemplo: verificar_prazo_processo(numero_processo='0001234-56.2024.8.26.0100')"
            ),
            args_schema=_VerificarPrazoProcessoArgs,
        ),
    ]
