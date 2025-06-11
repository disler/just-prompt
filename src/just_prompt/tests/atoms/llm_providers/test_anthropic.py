"""
Tests for Anthropic provider.
"""

import pytest
import os
from dotenv import load_dotenv
from just_prompt.atoms.llm_providers import anthropic

# Load environment variables
load_dotenv()

# Skip tests if API key not available
if not os.environ.get("ANTHROPIC_API_KEY"):
    pytest.skip("Anthropic API key not available", allow_module_level=True)


def test_list_models():
    """Test listing Anthropic models."""
    models = anthropic.list_models()
    
    # Assertions
    assert isinstance(models, list)
    assert len(models) > 0
    assert all(isinstance(model, str) for model in models)
    
    # Check for at least one expected model
    claude_models = [model for model in models if "claude" in model.lower()]
    assert len(claude_models) > 0, "No Claude models found"


def test_prompt():
    """Test sending prompt to Anthropic."""
    # Use the correct model name from the available models
    response = anthropic.prompt("What is the capital of France?", "claude-3-5-haiku-20241022")
    
    # Assertions
    assert isinstance(response, str)
    assert len(response) > 0
    assert "paris" in response.lower() or "Paris" in response


def test_parse_thinking_suffix():
    """Test parsing thinking suffix from model names."""
    # Test cases with no suffix
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet") == ("claude-3-7-sonnet", 0)
    assert anthropic.parse_thinking_suffix("claude-3-5-haiku-20241022") == ("claude-3-5-haiku-20241022", 0)
    
    # Test cases with supported claude-3-7 model and k suffixes
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet-20250219:1k") == ("claude-3-7-sonnet-20250219", 1024)
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet-20250219:4k") == ("claude-3-7-sonnet-20250219", 4096)
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet-20250219:15k") == ("claude-3-7-sonnet-20250219", 15360)  # 15*1024=15360 < 16000
    
    # Test cases with supported claude-4 models and k suffixes  
    assert anthropic.parse_thinking_suffix("claude-opus-4-20250514:1k") == ("claude-opus-4-20250514", 1024)
    assert anthropic.parse_thinking_suffix("claude-opus-4-20250514:4k") == ("claude-opus-4-20250514", 4096)
    assert anthropic.parse_thinking_suffix("claude-sonnet-4-20250514:1k") == ("claude-sonnet-4-20250514", 1024)
    assert anthropic.parse_thinking_suffix("claude-sonnet-4-20250514:8k") == ("claude-sonnet-4-20250514", 8192)
    
    # Test cases with supported models and numeric suffixes
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet-20250219:1024") == ("claude-3-7-sonnet-20250219", 1024)
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet-20250219:4096") == ("claude-3-7-sonnet-20250219", 4096)
    assert anthropic.parse_thinking_suffix("claude-opus-4-20250514:8000") == ("claude-opus-4-20250514", 8000)
    assert anthropic.parse_thinking_suffix("claude-sonnet-4-20250514:2048") == ("claude-sonnet-4-20250514", 2048)
    
    # Test cases with non-supported model
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet:1k") == ("claude-3-7-sonnet", 0)
    assert anthropic.parse_thinking_suffix("claude-3-5-haiku:4k") == ("claude-3-5-haiku", 0)
    
    # Test cases with out-of-range values (should adjust to valid range)
    assert anthropic.parse_thinking_suffix("claude-3-7-sonnet-20250219:500") == ("claude-3-7-sonnet-20250219", 1024)  # Below min 1024, should use 1024
    assert anthropic.parse_thinking_suffix("claude-opus-4-20250514:20000") == ("claude-opus-4-20250514", 16000)  # Above max 16000, should use 16000


def test_prompt_with_thinking():
    """Test sending prompt with thinking enabled."""
    # Test with 1k thinking tokens on the supported model
    response = anthropic.prompt("What is the capital of Spain?", "claude-3-7-sonnet-20250219:1k")
    
    # Assertions
    assert isinstance(response, str)
    assert len(response) > 0
    assert "madrid" in response.lower() or "Madrid" in response
    
    # Test with 2k thinking tokens on the supported model
    response = anthropic.prompt("What is the capital of Germany?", "claude-3-7-sonnet-20250219:2k")
    
    # Assertions
    assert isinstance(response, str)
    assert len(response) > 0
    assert "berlin" in response.lower() or "Berlin" in response
    
    # Test with out-of-range but auto-corrected thinking tokens
    response = anthropic.prompt("What is the capital of Italy?", "claude-3-7-sonnet-20250219:500")
    
    # Assertions (should still work with a corrected budget of 1024)
    assert isinstance(response, str)
    assert len(response) > 0
    assert "rome" in response.lower() or "Rome" in response