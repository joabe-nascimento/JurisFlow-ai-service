"""Tools customizadas para o agente jurídico."""

from datetime import datetime, timedelta
from typing import Optional

from langchain_core.tools import tool

from app.rag.langchain_store import langchain_rag_store


@tool
def calcular_prazo(
    data_inicial: str,
    dias_corridos: Optional[int] = None,
    dias_uteis: Optional[int] = None
) -> str:
    """
    Calcula prazo processual a partir de uma data.
    
    Args:
        data_inicial: Data inicial no formato DD/MM/YYYY
        dias_corridos: Número de dias corridos a adicionar (opcional)
        dias_uteis: Número de dias úteis a adicionar (opcional)
    
    Returns:
        Data final calculada e explicação
    
    Exemplos:
        - calcular_prazo("01/01/2024", dias_corridos=15)
        - calcular_prazo("01/01/2024", dias_uteis=15)
    """
    try:
        # Parse data inicial
        data = datetime.strptime(data_inicial, "%d/%m/%Y")
        
        if dias_corridos:
            data_final = data + timedelta(days=dias_corridos)
            return (
                f"Data inicial: {data_inicial}\n"
                f"Prazo: {dias_corridos} dias corridos\n"
                f"Data final: {data_final.strftime('%d/%m/%Y')}\n"
                f"Observação: Dias corridos incluem sábados, domingos e feriados."
            )
        
        elif dias_uteis:
            # Simplificado: considera apenas sábado/domingo (não feriados)
            dias_adicionados = 0
            data_atual = data
            
            while dias_adicionados < dias_uteis:
                data_atual += timedelta(days=1)
                if data_atual.weekday() < 5:  # 0-4 = segunda-sexta
                    dias_adicionados += 1
            
            return (
                f"Data inicial: {data_inicial}\n"
                f"Prazo: {dias_uteis} dias úteis\n"
                f"Data final: {data_atual.strftime('%d/%m/%Y')}\n"
                f"Observação: Considera apenas dias úteis (exclui sábados/domingos). "
                f"Feriados não foram considerados - verifique calendário oficial."
            )
        
        else:
            return "Erro: especifique dias_corridos OU dias_uteis."
    
    except ValueError as e:
        return f"Erro ao processar data: {e}. Use formato DD/MM/YYYY."


@tool
def buscar_conhecimento(query: str, escritorio_id: str = "default") -> str:
    """
    Busca conhecimento jurídico na base RAG do escritório.
    
    Args:
        query: Pergunta ou termo de busca
        escritorio_id: ID do escritório (default: "default")
    
    Returns:
        Conhecimento relevante encontrado
    
    Exemplos:
        - buscar_conhecimento("prazo apelação")
        - buscar_conhecimento("LGPD obrigações")
    """
    result = langchain_rag_store.search(escritorio_id, query, limit=3)
    
    if not result.chunks:
        return f"Nenhum conhecimento encontrado para: {query}"
    
    output = f"Encontrados {result.total_matches} resultados para '{query}':\n\n"
    
    for i, chunk in enumerate(result.chunks, 1):
        output += f"{i}. {chunk.document_title} (score: {chunk.score:.1f})\n"
        output += f"   {chunk.content[:200]}...\n\n"
    
    return output


@tool
def buscar_jurisprudencia(termo: str, tribunal: str = "STJ") -> str:
    """
    Busca jurisprudência simulada (demonstração - em produção integraria com APIs de tribunais).
    
    Args:
        termo: Termo de busca (ex: "dano moral", "LGPD")
        tribunal: Tribunal (STJ, STF, TJ-SP, etc.)
    
    Returns:
        Jurisprudência encontrada (simulada)
    
    Exemplos:
        - buscar_jurisprudencia("dano moral", "STJ")
        - buscar_jurisprudencia("LGPD", "STF")
    """
    # Simulação - em produção integraria com:
    # - API do STJ/STF
    # - JusBrasil
    # - Escavador
    
    jurisprudencias_simuladas = {
        "dano moral": [
            {
                "tribunal": "STJ",
                "numero": "REsp 1.234.567/SP",
                "ementa": "DANO MORAL. Quantum indenizatório. Razoabilidade e proporcionalidade. "
                          "O valor da indenização por dano moral deve observar os princípios da "
                          "razoabilidade e proporcionalidade, considerando a extensão do dano e "
                          "capacidade econômica das partes.",
            },
        ],
        "lgpd": [
            {
                "tribunal": "STJ",
                "numero": "REsp 1.987.654/RJ",
                "ementa": "LGPD. Tratamento de dados pessoais. Consentimento. A coleta e tratamento "
                          "de dados pessoais sem consentimento expresso do titular configura violação "
                          "à Lei 13.709/2018, ensejando responsabilização civil.",
            },
        ],
        "default": [
            {
                "tribunal": tribunal,
                "numero": "Simulado 123/2024",
                "ementa": f"Resultado simulado para '{termo}'. Em produção, esta tool integraria "
                          f"com APIs oficiais de tribunais (STJ, STF, TJs) para retornar "
                          f"jurisprudência real.",
            },
        ],
    }
    
    termo_lower = termo.lower()
    resultados = jurisprudencias_simuladas.get(
        termo_lower,
        jurisprudencias_simuladas["default"]
    )
    
    output = f"🔍 Jurisprudência - {tribunal} - '{termo}'\n\n"
    
    for i, juris in enumerate(resultados, 1):
        output += f"{i}. {juris['numero']}\n"
        output += f"   Tribunal: {juris['tribunal']}\n"
        output += f"   Ementa: {juris['ementa']}\n\n"
    
    output += "⚠️ ATENÇÃO: Resultados simulados para demonstração. Em produção, integraria com APIs oficiais."
    
    return output


@tool
def calcular_honorarios(
    valor_causa: float,
    tipo_acao: str = "cível",
    percentual_exito: Optional[float] = None
) -> str:
    """
    Calcula honorários advocatícios baseado na Tabela OAB.
    
    Args:
        valor_causa: Valor da causa em R$
        tipo_acao: Tipo de ação (cível, trabalhista, consultoria)
        percentual_exito: Percentual de êxito (10-30%)
    
    Returns:
        Cálculo de honorários
    
    Exemplos:
        - calcular_honorarios(50000, "cível")
        - calcular_honorarios(100000, "trabalhista", 20)
    """
    # Tabela simplificada OAB (varia por seccional)
    tabela = {
        "cível": {"min": 0.10, "max": 0.20},  # 10-20%
        "trabalhista": {"min": 0.15, "max": 0.25},  # 15-25%
        "consultoria": {"min": 0.08, "max": 0.15},  # 8-15%
    }
    
    tipo_lower = tipo_acao.lower()
    if tipo_lower not in tabela:
        return f"Tipo de ação '{tipo_acao}' não reconhecido. Use: cível, trabalhista, consultoria."
    
    config = tabela[tipo_lower]
    
    # Honorários contratuais
    min_contratual = valor_causa * config["min"]
    max_contratual = valor_causa * config["max"]
    
    output = f"💰 Cálculo de Honorários\n\n"
    output += f"Valor da Causa: R$ {valor_causa:,.2f}\n"
    output += f"Tipo de Ação: {tipo_acao.title()}\n\n"
    output += f"Honorários Contratuais (Tabela OAB):\n"
    output += f"  Mínimo: R$ {min_contratual:,.2f} ({config['min']*100:.0f}%)\n"
    output += f"  Máximo: R$ {max_contratual:,.2f} ({config['max']*100:.0f}%)\n\n"
    
    if percentual_exito:
        if not (10 <= percentual_exito <= 30):
            output += "⚠️ Percentual de êxito deve estar entre 10% e 30%.\n"
        else:
            exito = valor_causa * (percentual_exito / 100)
            output += f"Honorários de Êxito ({percentual_exito:.0f}%):\n"
            output += f"  Valor: R$ {exito:,.2f}\n"
    
    output += "\n📌 Observação: Valores baseados em tabela simplificada. "
    output += "Consulte tabela da OAB da sua seccional para valores precisos."
    
    return output


# Lista de tools para o agent
legal_tools = [
    calcular_prazo,
    buscar_conhecimento,
    buscar_jurisprudencia,
    calcular_honorarios,
]
