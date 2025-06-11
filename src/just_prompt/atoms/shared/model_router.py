"""
Model router for dispatching requests to the appropriate provider.
"""

import logging
from typing import List, Dict, Any, Optional
import importlib
from .utils import split_provider_and_model
from .data_types import ModelProviders

logger = logging.getLogger(__name__)


class ModelRouter:
    """
    Routes requests to the appropriate provider based on the model string.
    """

    @staticmethod
    def validate_and_correct_model(provider_name: str, model_name: str) -> str:
        """
        Validate a model name against available models for a provider, and correct it if needed.

        Args:
            provider_name: Provider name (full name)
            model_name: Model name to validate and potentially correct

        Returns:
            Validated and potentially corrected model name
        """
        # Early return for our thinking token models to bypass validation
        thinking_models = [
            "claude-3-7-sonnet-20250219",
            "claude-opus-4-20250514", 
            "claude-sonnet-4-20250514",
            "gemini-2.5-flash-preview-04-17"
        ]
        if any(thinking_model in model_name for thinking_model in thinking_models):
            return model_name

        try:
            # Import the provider module
            provider_module_name = f"just_prompt.atoms.llm_providers.{provider_name}"
            provider_module = importlib.import_module(provider_module_name)

            # Get available models
            available_models = provider_module.list_models()

            # Check if model is in available models
            if model_name in available_models:
                return model_name

            # Model needs correction - use the default correction model
            import os

            correction_model = os.environ.get(
                "CORRECTION_MODEL", "anthropic:claude-3-7-sonnet-20250219"
            )

            # Use magic model correction
            corrected_model = ModelRouter.magic_model_correction(
                provider_name, model_name, correction_model
            )

            if corrected_model != model_name:
                logger.info(
                    f"Corrected model name from '{model_name}' to '{corrected_model}' for provider '{provider_name}'"
                )
                return corrected_model

            return model_name
        except Exception as e:
            logger.warning(
                f"Error validating model '{model_name}' for provider '{provider_name}': {e}"
            )
            return model_name

    @staticmethod
    def route_prompt(model_string: str, text: str) -> str:
        """
        Route a prompt to the appropriate provider.

        Args:
            model_string: String in format "provider:model"
            text: The prompt text

        Returns:
            Response from the model
        """
        provider_prefix, model = split_provider_and_model(model_string)
        provider = ModelProviders.from_name(provider_prefix)

        if not provider:
            raise ValueError(f"Unknown provider prefix: {provider_prefix}")

        # Validate and potentially correct the model name
        validated_model = ModelRouter.validate_and_correct_model(
            provider.full_name, model
        )

        # Import the appropriate provider module
        try:
            module_name = f"just_prompt.atoms.llm_providers.{provider.full_name}"
            provider_module = importlib.import_module(module_name)

            # Call the prompt function
            return provider_module.prompt(text, validated_model)
        except ImportError as e:
            logger.error(f"Failed to import provider module: {e}")
            raise ValueError(f"Provider not available: {provider.full_name}")
        except Exception as e:
            logger.error(f"Error routing prompt to {provider.full_name}: {e}")
            raise

    @staticmethod
    def route_list_models(provider_name: str) -> List[str]:
        """
        Route a list_models request to the appropriate provider.

        Args:
            provider_name: Provider name (full or short)

        Returns:
            List of model names
        """
        provider = ModelProviders.from_name(provider_name)

        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        # Import the appropriate provider module
        try:
            module_name = f"just_prompt.atoms.llm_providers.{provider.full_name}"
            provider_module = importlib.import_module(module_name)

            # Call the list_models function
            return provider_module.list_models()
        except ImportError as e:
            logger.error(f"Failed to import provider module: {e}")
            raise ValueError(f"Provider not available: {provider.full_name}")
        except Exception as e:
            logger.error(f"Error listing models for {provider.full_name}: {e}")
            raise

    @staticmethod
    def magic_model_correction(provider: str, model: str, correction_model: str) -> str:
        """
        Correct a model name using a correction AI model if needed.

        Args:
            provider: Provider name
            model: Original model name
            correction_model: Model to use for the correction llm prompt, e.g. "o:gpt-4o-mini"

        Returns:
            Corrected model name
        """
        provider_module_name = f"just_prompt.atoms.llm_providers.{provider}"

        try:
            provider_module = importlib.import_module(provider_module_name)
            available_models = provider_module.list_models()

            # If model is already in available models, no correction needed
            if model in available_models:
                logger.info(f"Using {provider} and {model}")
                return model

            # Model needs correction - use correction model to correct it
            correction_provider, correction_model_name = split_provider_and_model(
                correction_model
            )
            correction_provider_enum = ModelProviders.from_name(correction_provider)

            if not correction_provider_enum:
                logger.warning(
                    f"Invalid correction model provider: {correction_provider}, skipping correction"
                )
                return model

            correction_module_name = (
                f"just_prompt.atoms.llm_providers.{correction_provider_enum.full_name}"
            )
            correction_module = importlib.import_module(correction_module_name)

            # Build prompt for the correction model
            prompt = f"""
Given a user-provided model name "{model}" for the provider "{provider}", and the list of actual available models below,
return the closest matching model name from the available models list.
Only return the exact model name, nothing else.

Available models: {', '.join(available_models)}
"""
            # Get correction from correction model
            corrected_model = correction_module.prompt(
                prompt, correction_model_name
            ).strip()

            # Verify the corrected model exists in the available models
            if corrected_model in available_models:
                logger.info(f"correction_model: {correction_model}")
                logger.info(f"models_prefixed_by_provider: {provider}:{model}")
                logger.info(f"corrected_model: {corrected_model}")
                return corrected_model
            else:
                logger.warning(
                    f"Corrected model {corrected_model} not found in available models"
                )
                return model

        except Exception as e:
            logger.error(f"Error in model correction: {e}")
            return model
