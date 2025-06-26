"""
Google Gemini provider implementation.
"""

import os
import re
from typing import List, Tuple
import logging
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Models that support thinking_budget
THINKING_ENABLED_MODELS = ["gemini-2.5-flash-preview-04-17"]


def parse_thinking_suffix(model: str) -> Tuple[str, int]:
    """
    Parse a model name to check for thinking token budget suffixes.
    Only works with the models in THINKING_ENABLED_MODELS.
    
    Supported formats:
    - model:1k, model:4k, model:24k
    - model:1000, model:1054, model:24576, etc. (any value between 0-24576)
    
    Args:
        model: The model name potentially with a thinking suffix
        
    Returns:
        Tuple of (base_model_name, thinking_budget)
        If no thinking suffix is found, thinking_budget will be 0
    """
    # First check if the model name contains a colon
    if ":" not in model:
        return model, 0
        
    # Split the model name on the first colon to handle models with multiple colons
    parts = model.split(":", 1)
    base_model = parts[0]
    suffix = parts[1] if len(parts) > 1 else ""
    
    # Check if the base model is in the supported models list
    if base_model not in THINKING_ENABLED_MODELS:
        logger.warning(f"Model {base_model} does not support thinking, ignoring thinking suffix")
        return base_model, 0
    
    # If there's no suffix or it's empty, return default values
    if not suffix:
        return base_model, 0
    
    # Check if the suffix is a valid number (with optional 'k' suffix)
    if re.match(r'^\d+k?$', suffix):
        # Extract the numeric part and handle 'k' multiplier
        if suffix.endswith('k'):
            try:
                thinking_budget = int(suffix[:-1]) * 1024
            except ValueError:
                logger.warning(f"Invalid thinking budget format: {suffix}, ignoring")
                return base_model, 0
        else:
            try:
                thinking_budget = int(suffix)
                # If a small number like 1, 4, 24 is provided, assume it's in "k" (multiply by 1024)
                if thinking_budget < 100:
                    thinking_budget *= 1024
            except ValueError:
                logger.warning(f"Invalid thinking budget format: {suffix}, ignoring")
                return base_model, 0
        
        # Adjust values outside the range
        if thinking_budget < 0:
            logger.warning(f"Thinking budget {thinking_budget} below minimum (0), using 0 instead")
            thinking_budget = 0
        elif thinking_budget > 24576:
            logger.warning(f"Thinking budget {thinking_budget} above maximum (24576), using 24576 instead")
            thinking_budget = 24576
            
        logger.info(f"Using thinking budget of {thinking_budget} tokens for model {base_model}")
        return base_model, thinking_budget
    else:
        # If suffix is not a valid number format, ignore it
        logger.warning(f"Invalid thinking budget format: {suffix}, ignoring")
        return base_model, 0


def prompt_with_thinking(text: str, model: str, thinking_budget: int) -> str:
    """
    Send a prompt to Google Gemini with thinking enabled and get a response.
    
    Args:
        text: The prompt text
        model: The base model name (without thinking suffix)
        thinking_budget: The token budget for thinking
        
    Returns:
        Response string from the model
    """
    try:
        logger.info(f"Sending prompt to Gemini model {model} with thinking budget {thinking_budget}")
        
        response = client.models.generate_content(
            model=model,
            contents=text,
            config=genai.types.GenerateContentConfig(
                thinking_config=genai.types.ThinkingConfig(
                    thinking_budget=thinking_budget
                )
            )
        )
        
        return response.text
    except Exception as e:
        logger.error(f"Error sending prompt with thinking to Gemini: {e}")
        raise ValueError(f"Failed to get response from Gemini with thinking: {str(e)}")


def prompt(text: str, model: str) -> str:
    """
    Send a prompt to Google Gemini and get a response.
    
    Automatically handles thinking suffixes in the model name (e.g., gemini-2.5-flash-preview-04-17:4k)
    
    Args:
        text: The prompt text
        model: The model name, optionally with thinking suffix
        
    Returns:
        Response string from the model
    """
    # Parse the model name to check for thinking suffixes
    base_model, thinking_budget = parse_thinking_suffix(model)
    
    # If thinking budget is specified, use prompt_with_thinking
    if thinking_budget > 0:
        return prompt_with_thinking(text, base_model, thinking_budget)
    
    # Otherwise, use regular prompt
    try:
        logger.info(f"Sending prompt to Gemini model: {base_model}")
        
        response = client.models.generate_content(
            model=base_model,
            contents=text
        )
        
        return response.text
    except Exception as e:
        logger.error(f"Error sending prompt to Gemini: {e}")
        raise ValueError(f"Failed to get response from Gemini: {str(e)}")


def list_models() -> List[str]:
    """
    List available Google Gemini models.
    
    Returns:
        List of model names
    """
    try:
        logger.info("Listing Gemini models")
        
        # Get the list of models using the correct API method
        models = []
        available_models = client.models.list()
        for m in available_models:
            # Check if the model supports content generation
            if hasattr(m, 'supported_generation_methods') and "generateContent" in m.supported_generation_methods:
                models.append(m.name)
            else:
                # If supported_generation_methods is not available, include all models
                models.append(m.name)
                
        # Format model names - strip the "models/" prefix if present
        formatted_models = [model.replace("models/", "") for model in models]
        
        return formatted_models
    except Exception as e:
        logger.error(f"Error listing Gemini models: {e}")
        # Throw the error instead of returning hardcoded list
        raise ValueError(f"Failed to list Gemini models: {str(e)}")