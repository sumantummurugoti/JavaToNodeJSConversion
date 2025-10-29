"""
LLM Providers Package
Factory for creating LLM provider instances
"""

import os
from typing import Optional
from .base import LLMProvider
from .gemini import GeminiProvider
from .ollama import OllamaProvider


def create_provider(provider_name: str, api_key: Optional[str] = None) -> LLMProvider:
    """
    Factory function to create LLM provider instances
    
    Args:
        provider_name: Name of the provider (gemini, ollama)
        api_key: API key for the provider (optional, will check env vars)
        
    Returns:
        LLMProvider: Instance of the requested provider
        
    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    provider_name = provider_name.lower()
    
    if provider_name == "gemini":
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Gemini API key required. "
            )
        return GeminiProvider(api_key)
    
    elif provider_name == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama3")
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        provider = OllamaProvider(model, host)
        
        # Check if model exists
        if not provider.check_model_exists():
            raise ValueError(
                f"Ollama model '{model}' not found. Make sure ollama is running"
            )
        
        return provider
    
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}\n"
            "Available providers: gemini, ollama"
        )


def list_available_providers() -> dict:
    """
    List all available providers and their status
    
    Returns:
        dict: Provider information
    """
    providers = {
        "gemini": {
            "name": "Google Gemini",
            "cost": "FREE",
            "key_required": True,
            "env_var": "GEMINI_API_KEY",
            "url": "https://makersuite.google.com/app/apikey"
        },
        "ollama": {
            "name": "Ollama (Local)",
            "cost": "FREE",
            "key_required": False,
            "env_var": None,
            "url": "https://ollama.ai"
        }
    }
    
    # Check which providers are configured
    for provider_id, info in providers.items():
        if info["env_var"]:
            info["configured"] = bool(os.getenv(info["env_var"]))
        else:
            # For Ollama, check if it's running
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                info["configured"] = response.status_code == 200
            except:
                info["configured"] = False
    
    return providers


__all__ = [
    'LLMProvider',
    'GeminiProvider',
    'OllamaProvider',
    'create_provider',
    'list_available_providers'
]