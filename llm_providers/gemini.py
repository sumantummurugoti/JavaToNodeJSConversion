"""
Google Gemini Provider - used FREE tier
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini API (Used FREE tier)"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        super().__init__(api_key)
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            api_key=api_key,
            temperature=0.1,
            max_output_tokens=2048,
        )
    
    def analyze_code(self, prompt: str) -> str:
        """
        Analyze code using Google Gemini API
        
        Args:
            prompt: Code analysis prompt
            
        Returns:
            str: Analysis result from Gemini
            
        Raises:
            Exception: If API call fails
        """
        try:
            resp = self.llm.invoke(prompt)
            content = getattr(resp, "content", resp)
            if isinstance(content, str):
                return content
            # Handle multi-part content (some Gemini responses)
            return "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        except Exception as e:
            raise Exception(f"Gemini (LangChain) error: {e}")
