"""
Prompt from file to file functionality for just-prompt.
"""

from typing import List
import logging
import os
from pathlib import Path
from .prompt_from_file import prompt_from_file
from ..atoms.shared.utils import DEFAULT_MODEL

logger = logging.getLogger(__name__)


def prompt_from_file_to_file(
    abs_file_path: str, models_prefixed_by_provider: List[str] = None, abs_output_dir: str = "."
) -> List[str]:
    """
    Read text from a file, send it as prompt to multiple models, and save responses to files.

    Args:
        abs_file_path: Absolute path to the text file (must be an absolute path, not relative)
        models_prefixed_by_provider: List of model strings in format "provider:model"
                                    If None, uses the DEFAULT_MODELS environment variable
        abs_output_dir: Absolute directory path to save response files (must be an absolute path, not relative)

    Returns:
        List of paths to the output files
    """
    # Validate output directory
    output_path = Path(abs_output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    if not output_path.is_dir():
        raise ValueError(f"Not a directory: {abs_output_dir}")

    # Get the base name of the input file
    input_file_name = Path(abs_file_path).stem

    # Get responses
    responses = prompt_from_file(abs_file_path, models_prefixed_by_provider)

    # Save responses to files
    output_files = []

    # Get the models that were actually used
    models_used = models_prefixed_by_provider
    if not models_used:
        default_models = os.environ.get("DEFAULT_MODELS", DEFAULT_MODEL)
        models_used = [model.strip() for model in default_models.split(",")]

    for i, (model_string, response) in enumerate(zip(models_used, responses)):
        # Sanitize model string for filename (replace colons with underscores)
        safe_model_name = model_string.replace(":", "_")

        # Create output filename with .md extension
        output_file = output_path / f"{input_file_name}_{safe_model_name}.md"

        # Write response to file as markdown
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response)
            output_files.append(str(output_file))
        except Exception as e:
            logger.error(f"Error writing response to {output_file}: {e}")
            output_files.append(f"Error: {str(e)}")

    return output_files
