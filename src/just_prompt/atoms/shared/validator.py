"""
Validation utilities for just-prompt.
"""

from typing import List, Dict, Optional, Tuple
import logging
import os
from .data_types import ModelProviders
from .utils import split_provider_and_model, get_api_key

logger = logging.getLogger(__name__)


def validate_models_prefixed_by_provider(models_prefixed_by_provider: List[str]) -> bool:
    """
    Validate that provider prefixes in model strings are valid.
    
    Args:
        models_prefixed_by_provider: List of model strings in format "provider:model"
        
    Returns:
        True if all valid, raises ValueError otherwise
    """
    if not models_prefixed_by_provider:
        raise ValueError("No models provided")
    
    for model_string in models_prefixed_by_provider:
        try:
            provider_prefix, model_name = split_provider_and_model(model_string)
            provider = ModelProviders.from_name(provider_prefix)
            if provider is None:
                raise ValueError(f"Unknown provider prefix: {provider_prefix}")
        except Exception as e:
            logger.error(f"Validation error for model string '{model_string}': {str(e)}")
            raise
    
    return True


def validate_provider(provider: str) -> bool:
    """
    Validate that a provider name is valid.
    
    Args:
        provider: Provider name (full or short)
        
    Returns:
        True if valid, raises ValueError otherwise
    """
    provider_enum = ModelProviders.from_name(provider)
    if provider_enum is None:
        raise ValueError(f"Unknown provider: {provider}")
    
    return True


def validate_provider_api_keys() -> Dict[str, bool]:
    """
    Validate that API keys are available for each provider.
    
    Returns:
        Dictionary mapping provider names to availability status (True if available, False otherwise)
    """
    available_providers = {}
    
    # Check API keys for each provider
    for provider in ModelProviders:
        provider_name = provider.full_name
        
        # Special case for Ollama which uses OLLAMA_HOST instead of an API key
        if provider_name == "ollama":
            host = os.environ.get("OLLAMA_HOST")
            is_available = host is not None and host.strip() != ""
            available_providers[provider_name] = is_available
        else:
            # Get API key
            api_key = get_api_key(provider_name)
            is_available = api_key is not None and api_key.strip() != ""
            available_providers[provider_name] = is_available
    
    return available_providers


def print_provider_availability(detailed: bool = True) -> None:
    """
    Print information about which providers are available based on API keys.
    
    Args:
        detailed: Whether to print detailed information about missing keys
    """
    availability = validate_provider_api_keys()
    
    available = [p for p, status in availability.items() if status]
    unavailable = [p for p, status in availability.items() if not status]
    
    # Print availability information
    logger.info(f"Available LLM providers: {', '.join(available)}")
    
    if detailed and unavailable:
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY", 
            "groq": "GROQ_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "ollama": "OLLAMA_HOST",
            "openrouter": "OPENROUTER_API_KEY"
        }
        
        logger.warning(f"The following providers are unavailable due to missing API keys:")
        for provider in unavailable:
            env_var = env_vars.get(provider)
            if env_var:
                logger.warning(f"  - {provider}: Missing environment variable {env_var}")
            else:
                logger.warning(f"  - {provider}: Missing configuration")