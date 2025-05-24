"""
Tests for list_providers functionality.
"""

import pytest
from just_prompt.molecules.list_providers import list_providers


def test_list_providers():
    """Test listing providers."""
    providers = list_providers()
    
    # Check basic structure
    assert isinstance(providers, list)
    assert len(providers) > 0
    assert all(isinstance(p, dict) for p in providers)
    
    # Check expected providers are present
    provider_names = [p["name"] for p in providers]
    assert "OPENAI" in provider_names
    assert "ANTHROPIC" in provider_names
    assert "GEMINI" in provider_names
    assert "GROQ" in provider_names
    assert "DEEPSEEK" in provider_names
    assert "OLLAMA" in provider_names
    
    # Check each provider has required fields
    for provider in providers:
        assert "name" in provider
        assert "full_name" in provider
        assert "short_name" in provider
        
        # Check full_name and short_name values
        if provider["name"] == "OPENAI":
            assert provider["full_name"] == "openai"
            assert provider["short_name"] == "o"
        elif provider["name"] == "ANTHROPIC":
            assert provider["full_name"] == "anthropic"
            assert provider["short_name"] == "a"
        elif provider["name"] == "GEMINI":
            assert provider["full_name"] == "gemini"
            assert provider["short_name"] == "g"
        elif provider["name"] == "GROQ":
            assert provider["full_name"] == "groq"
            assert provider["short_name"] == "q"
        elif provider["name"] == "DEEPSEEK":
            assert provider["full_name"] == "deepseek"
            assert provider["short_name"] == "d"
        elif provider["name"] == "OLLAMA":
            assert provider["full_name"] == "ollama"
            assert provider["short_name"] == "l"
