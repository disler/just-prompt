"""
Test OpenRouter provider implementation.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import the module to test
from just_prompt.atoms.llm_providers import openrouter


@pytest.fixture
def mock_requests():
    """
    Fixture to mock requests module for testing API calls.
    """
    with patch("just_prompt.atoms.llm_providers.openrouter.requests") as mock_requests:
        # Mock successful response for prompt
        mock_prompt_response = MagicMock()
        mock_prompt_response.status_code = 200
        mock_prompt_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Mock response from OpenRouter"
                    }
                }
            ]
        }
        
        # Mock successful response for list_models
        mock_models_response = MagicMock()
        mock_models_response.status_code = 200
        mock_models_response.json.return_value = {
            "data": [
                {"id": "anthropic/claude-3-opus"},
                {"id": "anthropic/claude-3-sonnet"},
                {"id": "openai/gpt-4o"}
            ]
        }
        
        # Configure the mock to return our mock responses
        mock_requests.post.return_value = mock_prompt_response
        mock_requests.get.return_value = mock_models_response
        
        yield mock_requests


@pytest.fixture
def mock_api_key():
    """
    Fixture to mock API key environment variable.
    """
    original_env = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "mock_api_key"
    yield
    if original_env:
        os.environ["OPENROUTER_API_KEY"] = original_env
    else:
        del os.environ["OPENROUTER_API_KEY"]


def test_prompt_with_mock(mock_requests, mock_api_key):
    """
    Test the prompt function using mocked requests.
    """
    # Call the function
    response = openrouter.prompt("Test prompt", "anthropic/claude-3-opus")
    
    # Check the result
    assert response == "Mock response from OpenRouter"
    
    # Verify the request was made correctly
    mock_requests.post.assert_called_once()
    args, kwargs = mock_requests.post.call_args
    assert args[0] == "https://openrouter.ai/api/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer mock_api_key"
    assert kwargs["json"]["model"] == "anthropic/claude-3-opus"
    assert kwargs["json"]["messages"][0]["content"] == "Test prompt"


def test_list_models_with_mock(mock_requests, mock_api_key):
    """
    Test the list_models function using mocked requests.
    """
    # Call the function
    models = openrouter.list_models()
    
    # Check the result
    assert len(models) == 3
    assert "anthropic/claude-3-opus" in models
    assert "anthropic/claude-3-sonnet" in models
    assert "openai/gpt-4o" in models
    
    # Verify the request was made correctly
    mock_requests.get.assert_called_once()
    args, kwargs = mock_requests.get.call_args
    assert args[0] == "https://openrouter.ai/api/v1/models"
    assert kwargs["headers"]["Authorization"] == "Bearer mock_api_key"


def test_prompt_without_api_key():
    """
    Test the prompt function when API key is missing.
    """
    # Temporarily remove the API key
    original_env = os.environ.get("OPENROUTER_API_KEY")
    if "OPENROUTER_API_KEY" in os.environ:
        del os.environ["OPENROUTER_API_KEY"]
    
    # Test that it raises an exception
    with pytest.raises(ValueError, match="OpenRouter API key not found"):
        openrouter.prompt("Test prompt", "anthropic/claude-3-opus")
    
    # Restore the original environment
    if original_env:
        os.environ["OPENROUTER_API_KEY"] = original_env