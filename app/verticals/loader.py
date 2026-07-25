"""
Carregador de configurações de vertical (nicho/domínio).

Cada vertical tem sua própria pasta com:
- config.yaml: configuração principal
- prompts/*.yaml: templates de prompts
- router.yaml: padrões de roteamento
- tools.yaml: definição de tools
- seed.yaml: base de conhecimento inicial
"""

from pathlib import Path
from typing import Any, Optional
import yaml
from functools import lru_cache


class VerticalConfig:
    """Configuração de um vertical (nicho/domínio)."""
    
    def __init__(self, vertical_id: str, config_dir: Path):
        self.vertical_id = vertical_id
        self.config_dir = config_dir
        self._config = self._load_yaml("config.yaml")
        self._router = self._load_yaml("router.yaml")
        self._tools = self._load_yaml("tools.yaml")
        self._seed = self._load_yaml("seed.yaml")
        self._prompts_cache: dict[str, dict] = {}
    
    def _load_yaml(self, filename: str) -> dict:
        """Carrega um arquivo YAML do vertical."""
        filepath = self.config_dir / filename
        if not filepath.exists():
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    def load_prompt(self, prompt_name: str) -> dict:
        """
        Carrega um template de prompt.
        
        Args:
            prompt_name: Nome do arquivo (com ou sem .yaml)
        
        Returns:
            Dict com name, description, temperature, max_tokens, system_prompt
        """
        if prompt_name in self._prompts_cache:
            return self._prompts_cache[prompt_name]
        
        if not prompt_name.endswith(".yaml"):
            prompt_name += ".yaml"
        
        prompt_path = self.config_dir / "prompts" / prompt_name
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt não encontrado: {prompt_path}")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)
        
        self._prompts_cache[prompt_name] = prompt_data
        return prompt_data
    
    @property
    def name(self) -> str:
        """Nome do produto/vertical."""
        return self._config.get("vertical", {}).get("name", "AI Platform")
    
    @property
    def description(self) -> str:
        """Descrição do vertical."""
        return self._config.get("vertical", {}).get("description", "")
    
    @property
    def domain(self) -> str:
        """Domínio do vertical (ex: Jurídico, Médico)."""
        return self._config.get("vertical", {}).get("domain", "Geral")
    
    @property
    def assistant_name(self) -> str:
        """Nome do assistente."""
        return self._config.get("assistant", {}).get("name", "Assistente")
    
    @property
    def assistant_role(self) -> str:
        """Role/papel do assistente."""
        return self._config.get("assistant", {}).get("role", "Assistente")
    
    @property
    def assistant_prompt_file(self) -> str:
        """Arquivo de prompt do assistente."""
        return self._config.get("assistant", {}).get("prompt_file", "assistant.yaml")
    
    @property
    def integration_api_url(self) -> str:
        """URL da API de integração."""
        from app.config import settings
        url = self._config.get("integration", {}).get("api_url", "")
        # Expande variável de ambiente se houver
        if "${" in url:
            import re
            import os
            # ${VAR:default}
            pattern = r'\$\{([^:}]+)(?::([^}]+))?\}'
            def replacer(match):
                var_name = match.group(1)
                default = match.group(2) or ""
                return os.getenv(var_name, default)
            url = re.sub(pattern, replacer, url)
        return url or settings.java_api_url
    
    @property
    def integration_timeout(self) -> float:
        """Timeout para chamadas da API de integração."""
        return float(self._config.get("integration", {}).get("timeout", 10.0))
    
    @property
    def chains(self) -> list[dict]:
        """Lista de chains disponíveis."""
        return self._config.get("chains", [])
    
    @property
    def agent_enabled(self) -> bool:
        """Se o agente está habilitado."""
        return self._config.get("agent", {}).get("enabled", True)
    
    @property
    def agent_max_iterations(self) -> int:
        """Máximo de iterações do agente."""
        return self._config.get("agent", {}).get("max_iterations", 10)
    
    @property
    def agent_verbose(self) -> bool:
        """Se o agente deve ser verbose."""
        return self._config.get("agent", {}).get("verbose", True)
    
    @property
    def router_intents(self) -> list[dict]:
        """Lista de intenções configuradas no router."""
        return self._router.get("intents", [])
    
    @property
    def tools(self) -> dict:
        """Configuração de tools."""
        return self._tools
    
    @property
    def seed_documents(self) -> list[dict]:
        """Documentos de seed da base de conhecimento."""
        return self._seed.get("documents", [])


@lru_cache(maxsize=10)
def load_vertical(vertical_id: str) -> VerticalConfig:
    """
    Carrega a configuração de um vertical.
    
    Args:
        vertical_id: ID do vertical (ex: 'legal', 'medical')
    
    Returns:
        VerticalConfig com todas as configurações
    
    Raises:
        FileNotFoundError se o vertical não existir
    """
    verticals_dir = Path(__file__).parent
    vertical_dir = verticals_dir / vertical_id
    
    if not vertical_dir.exists():
        raise FileNotFoundError(
            f"Vertical '{vertical_id}' não encontrado em {verticals_dir}. "
            f"Verifique se a pasta {vertical_dir} existe."
        )
    
    return VerticalConfig(vertical_id, vertical_dir)


def get_current_vertical() -> VerticalConfig:
    """
    Retorna o vertical configurado em AI_VERTICAL.
    
    Returns:
        VerticalConfig do vertical atual
    """
    from app.config import settings
    return load_vertical(settings.ai_vertical)


def list_available_verticals() -> list[str]:
    """
    Lista todos os verticais disponíveis.
    
    Returns:
        Lista de IDs de verticais
    """
    verticals_dir = Path(__file__).parent
    return [
        d.name
        for d in verticals_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / "config.yaml").exists()
    ]
