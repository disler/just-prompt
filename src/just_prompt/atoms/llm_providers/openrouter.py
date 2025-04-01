"""
OpenRouter provider implementation.
"""

import os
import requests
from typing import List
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1"

# API key from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")


def prompt(text: str, model: str) -> str:
    """
    Send a prompt to OpenRouter and get a response.

    Args:
        text: The prompt text
        model: The model name

    Returns:
        Response string from the model
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key not found in environment variables")

    try:
        logger.info(f"Sending prompt to OpenRouter model: {model}")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": text}]
        }
        
        response = requests.post(
            f"{OPENROUTER_API_URL}/chat/completions", 
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            logger.error(f"Error from OpenRouter API: {response.status_code}, {response.text}")
            raise ValueError(f"OpenRouter API returned error: {response.status_code}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    except Exception as e:
        logger.error(f"Error sending prompt to OpenRouter: {e}")
        raise ValueError(f"Failed to get response from OpenRouter: {str(e)}")


def list_models() -> List[str]:
    """
    List available OpenRouter models.

    Returns:
        List of model names
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key not found in environment variables")

    try:
        logger.info("Listing OpenRouter models")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{OPENROUTER_API_URL}/models", 
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Error from OpenRouter API: {response.status_code}, {response.text}")
            raise ValueError(f"OpenRouter API returned error: {response.status_code}")
        
        result = response.json()
        # Extract model IDs from the response
        models = [model["id"] for model in result["data"]]
        
        return models
    
    except Exception as e:
        logger.error(f"Error listing OpenRouter models: {e}")
        raise ValueError(f"Failed to list OpenRouter models: {str(e)}")