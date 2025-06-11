"""
CEO and Board prompt functionality for just-prompt.
"""

from typing import List
import logging
import os
from pathlib import Path
from .prompt_from_file_to_file import prompt_from_file_to_file
from .prompt import prompt
from ..atoms.shared.utils import DEFAULT_MODEL

logger = logging.getLogger(__name__)

# Default CEO model
DEFAULT_CEO_MODEL = "openai:o3"

# Default CEO decision prompt template
DEFAULT_CEO_DECISION_PROMPT = """
<purpose>
    You are a CEO of a company. You are given a list of responses from your board of directors. Your job is to take in the original question prompt, and each of the board members' responses, and choose the best direction for your company.
</purpose>
<instructions>
    <instruction>Each board member has proposed an answer to the question posed in the prompt.</instruction>
    <instruction>Given the original question prompt, and each of the board members' responses, choose the best answer.</instruction>
    <instruction>Tally the votes of the board members, choose the best direction, and explain why you chose it.</instruction>
    <instruction>To preserve anonymity, we will use model names instead of real names of your board members. When responding, use the model names in your response.</instruction>
    <instruction>As a CEO, you breakdown the decision into several categories including: risk, reward, timeline, and resources. In addition to these guiding categories, you also consider the board members' expertise and experience. As a bleeding edge CEO, you also invent new dimensions of decision making to help you make the best decision for your company.</instruction>
    <instruction>Your final CEO response should be in markdown format with a comprehensive explanation of your decision. Start the top of the file with a title that says "CEO Decision", include a table of contents, briefly describe the question/problem at hand then dive into several sections. One of your first sections should be a quick summary of your decision, then breakdown each of the boards decisions into sections with your commentary on each. Where we lead into your decision with the categories of your decision making process, and then we lead into your final decision.</instruction>
</instructions>

<original-question>{original_prompt}</original-question>

<board-decisions>
{board_responses}
</board-decisions>
"""


def ceo_and_board_prompt(
    abs_from_file: str,
    abs_output_dir: str = ".",
    models_prefixed_by_provider: List[str] = None,
    ceo_model: str = DEFAULT_CEO_MODEL,
    ceo_decision_prompt: str = DEFAULT_CEO_DECISION_PROMPT
) -> str:
    """
    Read text from a file, send it as prompt to multiple 'board member' models,
    and then have a 'CEO' model make a decision based on the responses.

    Args:
        abs_from_file: Absolute path to the text file containing the original prompt (must be an absolute path, not relative)
        abs_output_dir: Absolute directory path to save response files (must be an absolute path, not relative)
        models_prefixed_by_provider: List of model strings in format "provider:model"
                                   to act as the board members
        ceo_model: Model to use for the CEO decision in format "provider:model"
        ceo_decision_prompt: Template for the CEO decision prompt

    Returns:
        Path to the CEO decision file
    """
    # Validate output directory
    output_path = Path(abs_output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    if not output_path.is_dir():
        raise ValueError(f"Not a directory: {abs_output_dir}")

    # Get the original prompt from the file
    try:
        with open(abs_from_file, 'r', encoding='utf-8') as f:
            original_prompt = f.read()
    except Exception as e:
        logger.error(f"Error reading file {abs_from_file}: {e}")
        raise ValueError(f"Error reading file: {str(e)}")

    # Step 1: Get board members' responses
    board_response_files = prompt_from_file_to_file(
        abs_file_path=abs_from_file,
        models_prefixed_by_provider=models_prefixed_by_provider,
        abs_output_dir=abs_output_dir
    )

    # Get the models that were actually used
    models_used = models_prefixed_by_provider
    if not models_used:
        default_models = os.environ.get("DEFAULT_MODELS", DEFAULT_MODEL)
        models_used = [model.strip() for model in default_models.split(",")]

    # Step 2: Read in the board responses
    board_responses_text = ""
    for i, file_path in enumerate(board_response_files):
        model_name = models_used[i].replace(":", "_")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                response_content = f.read()
                board_responses_text += f"""
<board-response>
    <model-name>{models_used[i]}</model-name>
    <response>{response_content}</response>
</board-response>
"""
        except Exception as e:
            logger.error(f"Error reading board response file {file_path}: {e}")
            board_responses_text += f"""
<board-response>
    <model-name>{models_used[i]}</model-name>
    <response>Error reading response: {str(e)}</response>
</board-response>
"""

    # Step 3: Prepare the CEO decision prompt
    final_ceo_prompt = ceo_decision_prompt.format(
        original_prompt=original_prompt,
        board_responses=board_responses_text
    )

    # Step 4: Save the CEO prompt to a file
    ceo_prompt_file = output_path / "ceo_prompt.xml"
    try:
        with open(ceo_prompt_file, "w", encoding="utf-8") as f:
            f.write(final_ceo_prompt)
    except Exception as e:
        logger.error(f"Error writing CEO prompt to {ceo_prompt_file}: {e}")
        raise ValueError(f"Error writing CEO prompt: {str(e)}")
    
    # Step 5: Get the CEO decision
    ceo_response = prompt(final_ceo_prompt, [ceo_model])[0]

    # Step 6: Write the CEO decision to a file
    ceo_output_file = output_path / "ceo_decision.md"
    try:
        with open(ceo_output_file, "w", encoding="utf-8") as f:
            f.write(ceo_response)
    except Exception as e:
        logger.error(f"Error writing CEO decision to {ceo_output_file}: {e}")
        raise ValueError(f"Error writing CEO decision: {str(e)}")

    return str(ceo_output_file)