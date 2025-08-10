"""
OpenAI provider implementation.
"""

"""OpenAI provider implementation with support for o‑series *reasoning effort* suffixes.

Supported suffixes (case‑insensitive): ``:low``, ``:medium``, ``:high`` on the
reasoning models ``o4-mini``, ``o3-mini`` and ``o3``.  When such a suffix is
present we use OpenAI's *Responses* API with the corresponding
``reasoning={"effort": <level>}`` parameter (if the SDK supports it).  If the
installed ``openai`` SDK is older and does not expose the ``responses``
resource, we gracefully fall back to the Chat Completions endpoint so that the
basic functionality (and our tests) still work.
"""

import os
import re
import logging
from typing import List, Tuple

from dotenv import load_dotenv

# Third‑party import guarded so that static analysis still works when the SDK
# is absent.
from openai import OpenAI  # type: ignore
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client once – reused across calls.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


_REASONING_ELIGIBLE_MODELS = {"o4-mini", "o3-mini", "o3", "gpt-5", "gpt-5-mini", "gpt-5-nano"}
_REASONING_LEVELS = {"low", "medium", "high"}


# Public so that tests can import.

def parse_reasoning_suffix(model: str) -> Tuple[str, str]:
    """Return (base_model, effort_level).

    If *model* is something like ``o4-mini:high`` (case‑insensitive) we return
    ("o4-mini", "high").  For all other inputs we return (_model_, "").
    """

    # Split once from the right so additional colons inside the *provider* part
    # are untouched (the caller already stripped the provider prefix).
    if ":" not in model:
        return model, ""

    base, suffix = model.rsplit(":", 1)

    suffix_lower = suffix.lower()

    if base in _REASONING_ELIGIBLE_MODELS and suffix_lower in _REASONING_LEVELS:
        return base, suffix_lower

    # Not a recognised reasoning pattern; treat the whole string as the model
    return model, ""


def _prompt_with_reasoning(text: str, model: str, effort: str) -> str:  # pragma: no cover – hits network
    """Call OpenAI *Responses* API with reasoning effort.

    Falls back transparently to chat completions if the installed SDK does not
    yet expose the *responses* resource.
    """

    if not effort:
        raise ValueError("effort must be 'low', 'medium', or 'high'")

    logger.info(
        "Sending prompt to OpenAI reasoning model %s with effort '%s'", model, effort
    )

    # Prefer the official Responses endpoint when present.
    if hasattr(client, "responses"):
        try:
            response = client.responses.create(
                model=model,
                reasoning={"effort": effort},
                input=[{"role": "user", "content": text}],
            )

            # The modern SDK returns .output_text
            output_text = getattr(response, "output_text", None)
            if output_text is not None:
                return output_text

            # Fallback path: maybe same shape as chat completions.
            if hasattr(response, "choices") and response.choices:
                return response.choices[0].message.content  # type: ignore[attr-defined]

            raise ValueError("Unexpected response format from OpenAI responses API")
        except Exception as exc:  # pragma: no cover – keep behaviour consistent
            logger.warning("Responses API failed (%s); falling back to chat", exc)

    # Fallback to chat completions – pass the reasoning level as a system
    # message so that, even without official support, the model can try to act
    # accordingly.  This keeps tests functional if the Responses API is not
    # available in the runtime environment.
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"Use {effort} reasoning effort before answering.",
                },
                {"role": "user", "content": text},
            ],
        )

        return response.choices[0].message.content  # type: ignore[attr-defined]
    except Exception as exc:
        logger.error("Error sending prompt to OpenAI (fallback chat): %s", exc)
        raise ValueError(f"Failed to get response from OpenAI: {exc}")


def prompt(text: str, model: str) -> str:
    """Main prompt entry‑point for the OpenAI provider.

    Handles the optional ``:low|:medium|:high`` suffix on reasoning models.
    Falls back to regular chat completions when no suffix is detected.
    """

    base_model, effort = parse_reasoning_suffix(model)

    if effort:
        return _prompt_with_reasoning(text, base_model, effort)

    # Regular chat completion path
    try:
        logger.info("Sending prompt to OpenAI model: %s", base_model)
        response = client.chat.completions.create(
            model=base_model,
            messages=[{"role": "user", "content": text}],
        )

        return response.choices[0].message.content  # type: ignore[attr-defined]
    except Exception as exc:
        logger.error("Error sending prompt to OpenAI: %s", exc)
        raise ValueError(f"Failed to get response from OpenAI: {exc}")


def list_models() -> List[str]:
    """
    List available OpenAI models.

    Returns:
        List of model names
    """
    try:
        logger.info("Listing OpenAI models")
        response = client.models.list()

        # Return all models without filtering
        models = [model.id for model in response.data]

        return models
    except Exception as exc:
        # Networking errors shouldn't break the caller – return a minimal hard‑coded list.
        logger.warning("Error listing OpenAI models via API (%s). Returning fallback list.", exc)
        return [
            "gpt-4o-mini",
            "o4-mini",
            "o3-mini",
            "o3",
            "text-davinci-003",
        ]
