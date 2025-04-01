"""
Data types and models for just-prompt MCP server.
"""

from enum import Enum


class ModelProviders(Enum):
    """
    Enum of supported model providers with their full and short names.
    """
    OPENAI = ("openai", "o")
    ANTHROPIC = ("anthropic", "a")
    GEMINI = ("gemini", "g") 
    GROQ = ("groq", "q")
    DEEPSEEK = ("deepseek", "d")
    OLLAMA = ("ollama", "l")
    OPENROUTER = ("openrouter", "r")
    
    def __init__(self, full_name, short_name):
        self.full_name = full_name
        self.short_name = short_name
        
    @classmethod
    def from_name(cls, name):
        """
        Get provider enum from full or short name.
        
        Args:
            name: The provider name (full or short)
            
        Returns:
            ModelProviders: The corresponding provider enum, or None if not found
        """
        for provider in cls:
            if provider.full_name == name or provider.short_name == name:
                return provider
        return None