"""
Ollama Local Provider
FREE - local LLM
"""

import requests
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama (To Use Local LLM)"""
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        super().__init__(None)  # No API key needed
        self.api_url = f"{host}/api/generate"
        self.model = model
        self.host = host
    
    def analyze_code(self, prompt: str) -> str:
        """
        Analyze code using local Ollama instance
        
        Args:
            prompt: Code analysis prompt
            
        Returns:
            str: Analysis result from Ollama
            
        Raises:
            Exception: If Ollama is not running or API call fails
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(self.api_url, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["response"]
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Cannot connect to Ollama at {self.host}. "
                "Make sure Ollama is running: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise Exception(
                "Ollama request timeout. The model might be too slow or processing a large request."
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Ollama returned unexpected format: {e}")
    
    def check_model_exists(self) -> bool:
        """Check if the model is downloaded"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return any(m["name"].startswith(self.model) for m in models)
        except:
            return False
