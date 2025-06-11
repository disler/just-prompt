"""
Anthropic provider implementation.
"""

import os
import re
import anthropic
from typing import List, Tuple
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def parse_thinking_suffix(model: str) -> Tuple[str, int]:
    """
    Parse a model name to check for thinking token budget suffixes.
    Only works with the claude-3-7-sonnet-20250219 model.
    
    Supported formats:
    - model:1k, model:4k, model:16k
    - model:1000, model:1054, model:1333, etc. (any value between 1024-16000)
    
    Args:
        model: The model name potentially with a thinking suffix
        
    Returns:
        Tuple of (base_model_name, thinking_budget)
        If no thinking suffix is found, thinking_budget will be 0
    """
    # Look for patterns like ":1k", ":4k", ":16k" or ":1000", ":1054", etc.
    pattern = r'^(.+?)(?::(\d+)k?)?$'
    match = re.match(pattern, model)
    
    if not match:
        return model, 0
    
    base_model = match.group(1)
    thinking_suffix = match.group(2)
    
    # Validate the model - only specific Claude models support thinking
    supported_thinking_models = [
        "claude-3-7-sonnet-20250219",
        "claude-opus-4-20250514", 
        "claude-sonnet-4-20250514"
    ]
    if base_model not in supported_thinking_models:
        logger.warning(f"Model {base_model} does not support thinking, ignoring thinking suffix")
        return base_model, 0
    
    if not thinking_suffix:
        return model, 0
    
    # Convert to integer
    try:
        thinking_budget = int(thinking_suffix)
        # If a small number like 1, 4, 16 is provided, assume it's in "k" (multiply by 1024)
        if thinking_budget < 100:
            thinking_budget *= 1024
            
        # Adjust values outside the range
        if thinking_budget < 1024:
            logger.warning(f"Thinking budget {thinking_budget} below minimum (1024), using 1024 instead")
            thinking_budget = 1024
        elif thinking_budget > 16000:
            logger.warning(f"Thinking budget {thinking_budget} above maximum (16000), using 16000 instead")
            thinking_budget = 16000
            
        logger.info(f"Using thinking budget of {thinking_budget} tokens for model {base_model}")
        return base_model, thinking_budget
    except ValueError:
        logger.warning(f"Invalid thinking budget format: {thinking_suffix}, ignoring")
        return base_model, 0


def prompt_with_thinking(text: str, model: str, thinking_budget: int) -> str:
    """
    Send a prompt to Anthropic Claude with thinking enabled and get a response.
    
    Args:
        text: The prompt text
        model: The base model name (without thinking suffix)
        thinking_budget: The token budget for thinking
        
    Returns:
        Response string from the model
    """
    try:
        # Ensure max_tokens is greater than thinking_budget
        # Documentation requires this: https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#max-tokens-and-context-window-size
        max_tokens = thinking_budget + 1000  # Adding 1000 tokens for the response
        
        logger.info(f"Sending prompt to Anthropic model {model} with thinking budget {thinking_budget}")
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget,
            },
            messages=[{"role": "user", "content": text}]
        )
        
        # Extract the response from the message content
        # Filter out thinking blocks and only get text blocks
        text_blocks = [block for block in message.content if block.type == "text"]
        
        if not text_blocks:
            raise ValueError("No text content found in response")
            
        return text_blocks[0].text
    except Exception as e:
        logger.error(f"Error sending prompt with thinking to Anthropic: {e}")
        raise ValueError(f"Failed to get response from Anthropic with thinking: {str(e)}")


def prompt(text: str, model: str) -> str:
    """
    Send a prompt to Anthropic Claude and get a response.
    
    Automatically handles thinking suffixes in the model name (e.g., claude-3-7-sonnet-20250219:4k)
    
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
        logger.info(f"Sending prompt to Anthropic model: {base_model}")
        message = client.messages.create(
            model=base_model, max_tokens=4096, messages=[{"role": "user", "content": text}]
        )

        # Extract the response from the message content
        # Get only text blocks
        text_blocks = [block for block in message.content if block.type == "text"]
        
        if not text_blocks:
            raise ValueError("No text content found in response")
            
        return text_blocks[0].text
    except Exception as e:
        logger.error(f"Error sending prompt to Anthropic: {e}")
        raise ValueError(f"Failed to get response from Anthropic: {str(e)}")


def list_models() -> List[str]:
    """
    List available Anthropic models.
    
    Returns:
        List of model names
    """
    try:
        logger.info("Listing Anthropic models")
        response = client.models.list()

        models = [model.id for model in response.data]
        return models
    except Exception as e:
        logger.error(f"Error listing Anthropic models: {e}")
        # Return some known models if API fails
        logger.info("Returning hardcoded list of known Anthropic models")
        return [
            "claude-3-7-sonnet",
            "claude-3-5-sonnet",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-haiku",
        ]