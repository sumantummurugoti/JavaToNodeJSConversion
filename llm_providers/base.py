"""
Base LLM Provider
Abstract base class for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    def analyze_code(self, prompt: str) -> str:
        """
        Analyze code using the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            str: The LLM response
        """
        raise NotImplementedError("Subclasses must implement analyze_code()")
    
    def get_provider_name(self) -> str:
        """Get the name of the provider"""
        return self.__class__.__name__.replace("Provider", "")
