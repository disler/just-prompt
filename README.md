# Just Prompt - A lightweight MCP server for LLM providers

`just-prompt` is a Model Control Protocol (MCP) server that provides a unified interface to various Large Language Model (LLM) providers including OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, and Ollama. See how we use the `ceo_and_board` tool to make [hard decisions easy with o3 here](https://youtu.be/LEMLntjfihA).

<img src="images/just-prompt-logo.png" alt="Just Prompt Logo" width="700" height="auto">

<img src="images/o3-as-a-ceo.png" alt="Just Prompt Logo" width="700" height="auto">


## Tools

The following MCP tools are available in the server:

- **`prompt`**: Send a prompt to multiple LLM models
  - Parameters:
    - `text`: The prompt text
    - `models_prefixed_by_provider` (optional): List of models with provider prefixes. If not provided, uses default models.

- **`prompt_from_file`**: Send a prompt from a file to multiple LLM models
  - Parameters:
    - `file`: Path to the file containing the prompt
    - `models_prefixed_by_provider` (optional): List of models with provider prefixes. If not provided, uses default models.

- **`prompt_from_file_to_file`**: Send a prompt from a file to multiple LLM models and save responses as markdown files
  - Parameters:
    - `file`: Path to the file containing the prompt
    - `models_prefixed_by_provider` (optional): List of models with provider prefixes. If not provided, uses default models.
    - `output_dir` (default: "."): Directory to save the response markdown files to

- **`ceo_and_board`**: Send a prompt to multiple 'board member' models and have a 'CEO' model make a decision based on their responses
  - Parameters:
    - `file`: Path to the file containing the prompt
    - `models_prefixed_by_provider` (optional): List of models with provider prefixes to act as board members. If not provided, uses default models.
    - `output_dir` (default: "."): Directory to save the response files and CEO decision
    - `ceo_model` (default: "openai:o3"): Model to use for the CEO decision in format "provider:model"

- **`list_providers`**: List all available LLM providers
  - Parameters: None

- **`list_models`**: List all available models for a specific LLM provider
  - Parameters:
    - `provider`: Provider to list models for (e.g., 'openai' or 'o')

## Provider Prefixes
> every model must be prefixed with the provider name
>
> use the short name for faster referencing

- `o` or `openai`: OpenAI 
  - `o:gpt-4o-mini`
  - `openai:gpt-4o-mini`
- `a` or `anthropic`: Anthropic 
  - `a:claude-3-5-haiku`
  - `anthropic:claude-3-5-haiku`
- `g` or `gemini`: Google Gemini 
  - `g:gemini-2.5-pro-exp-03-25`
  - `gemini:gemini-2.5-pro-exp-03-25`
- `q` or `groq`: Groq 
  - `q:llama-3.1-70b-versatile`
  - `groq:llama-3.1-70b-versatile`
- `d` or `deepseek`: DeepSeek 
  - `d:deepseek-coder`
  - `deepseek:deepseek-coder`
- `l` or `ollama`: Ollama 
  - `l:llama3.1`
  - `ollama:llama3.1`

## Features

- Unified API for multiple LLM providers
- Support for text prompts from strings or files
- Run multiple models in parallel
- Automatic model name correction using the first model in the `--default-models` list
- Ability to save responses to files
- Easy listing of available providers and models

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/just-prompt.git
cd just-prompt

# Install with pip
uv sync
```

### Environment Variables

Create a `.env` file with your API keys (you can copy the `.env.sample` file):

```bash
cp .env.sample .env
```

Then edit the `.env` file to add your API keys (or export them in your shell):

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OLLAMA_HOST=http://localhost:11434
```

## Claude Code Installation
> In all these examples, replace the directory with the path to the just-prompt directory.

Default models set to `openai:o3:high`, `openai:o4-mini:high`, `anthropic:claude-3-7-sonnet-20250219:4k`, `gemini:gemini-2.5-pro-preview-03-25`, and `gemini:gemini-2.5-flash-preview-04-17`.

If you use Claude Code right out of the repository you can see in the .mcp.json file we set the default models to...

```
{
  "mcpServers": {
    "just-prompt": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        ".",
        "run",
        "just-prompt",
        "--default-models",
        "openai:o3:high,openai:o4-mini:high,anthropic:claude-3-7-sonnet-20250219:4k,gemini:gemini-2.5-pro-preview-03-25,gemini:gemini-2.5-flash-preview-04-17"
      ],
      "env": {}
    }
  }
}
```

The `--default-models` parameter sets the models to use when none are explicitly provided to the API endpoints. The first model in the list is also used for model name correction when needed. This can be a list of models separated by commas.

When starting the server, it will automatically check which API keys are available in your environment and inform you which providers you can use. If a key is missing, the provider will be listed as unavailable, but the server will still start and can be used with the providers that are available.

### Using `mcp add-json`

Copy this and paste it into claude code with BUT don't run until you copy the json

```
claude mcp add just-prompt "$(pbpaste)"
```

JSON to copy

```
{
    "command": "uv",
    "args": ["--directory", ".", "run", "just-prompt"]
}
```

With a custom default model set to `openai:gpt-4o`.

```
{
    "command": "uv",
    "args": ["--directory", ".", "run", "just-prompt", "--default-models", "openai:gpt-4o"]
}
```

With multiple default models:

```
{
    "command": "uv",
    "args": ["--directory", ".", "run", "just-prompt", "--default-models", "openai:o3:high,openai:o4-mini:high,anthropic:claude-3-7-sonnet-20250219:4k,gemini:gemini-2.5-pro-preview-03-25,gemini:gemini-2.5-flash-preview-04-17"]
}
```

### Using `mcp add` with project scope

```bash
# With default models
claude mcp add just-prompt -s project \
  -- \
    uv --directory . \
    run just-prompt

# With custom default model
claude mcp add just-prompt -s project \
  -- \
  uv --directory . \
  run just-prompt --default-models "openai:gpt-4o"

# With multiple default models
claude mcp add just-prompt -s user \
  -- \
  uv --directory . \
  run just-prompt --default-models "openai:o3:high,openai:o4-mini:high,anthropic:claude-3-7-sonnet-20250219:4k,gemini:gemini-2.5-pro-preview-03-25,gemini:gemini-2.5-flash-preview-04-17:4k"
```


## `mcp remove`

claude mcp remove just-prompt

## Running Tests

```bash
uv run pytest
```

## Codebase Structure

```
.
├── ai_docs/                   # Documentation for AI model details
│   ├── extending_thinking_sonny.md
│   ├── llm_providers_details.xml
│   ├── openai-reasoning-effort.md
│   └── pocket-pick-mcp-server-example.xml
├── example_outputs/           # Example outputs from different models
├── list_models.py             # Script to list available LLM models
├── prompts/                   # Example prompt files
├── pyproject.toml             # Python project configuration
├── specs/                     # Project specifications
│   ├── init-just-prompt.md
│   ├── new-tool-llm-as-a-ceo.md
│   └── oai-reasoning-levels.md
├── src/                       # Source code directory
│   └── just_prompt/
│       ├── __init__.py
│       ├── __main__.py
│       ├── atoms/             # Core components
│       │   ├── llm_providers/ # Individual provider implementations
│       │   │   ├── anthropic.py
│       │   │   ├── deepseek.py
│       │   │   ├── gemini.py
│       │   │   ├── groq.py
│       │   │   ├── ollama.py
│       │   │   └── openai.py
│       │   └── shared/        # Shared utilities and data types
│       │       ├── data_types.py
│       │       ├── model_router.py
│       │       ├── utils.py
│       │       └── validator.py
│       ├── molecules/         # Higher-level functionality
│       │   ├── ceo_and_board_prompt.py
│       │   ├── list_models.py
│       │   ├── list_providers.py
│       │   ├── prompt.py
│       │   ├── prompt_from_file.py
│       │   └── prompt_from_file_to_file.py
│       ├── server.py          # MCP server implementation
│       └── tests/             # Test directory
│           ├── atoms/         # Tests for atoms
│           │   ├── llm_providers/
│           │   └── shared/
│           └── molecules/     # Tests for molecules
│               ├── test_ceo_and_board_prompt.py
│               ├── test_list_models.py
│               ├── test_list_providers.py
│               ├── test_prompt.py
│               ├── test_prompt_from_file.py
│               └── test_prompt_from_file_to_file.py
└── ultra_diff_review/         # Diff review outputs
```

## Context Priming
READ README.md, pyproject.toml, then run git ls-files, and 'eza --git-ignore --tree' to understand the context of the project.

# Reasoning Effort with OpenAI o‑Series

For OpenAI o‑series reasoning models (`o4-mini`, `o3-mini`, `o3`) you can
control how much *internal* reasoning the model performs before producing a
visible answer.

Append one of the following suffixes to the model name (after the *provider*
prefix):

* `:low`   – minimal internal reasoning (faster, cheaper)
* `:medium` – balanced (default if omitted)
* `:high`  – thorough reasoning (slower, more tokens)

Examples:

* `openai:o4-mini:low`
* `o:o4-mini:high`

When a reasoning suffix is present, **just‑prompt** automatically switches to
the OpenAI *Responses* API (when available) and sets the corresponding
`reasoning.effort` parameter.  If the installed OpenAI SDK is older, it
gracefully falls back to the Chat Completions endpoint and embeds an internal
system instruction to approximate the requested effort level.

# Thinking Tokens with Claude

The Anthropic Claude model `claude-3-7-sonnet-20250219` supports extended thinking capabilities using thinking tokens. This allows Claude to do more thorough thought processes before answering.

You can enable thinking tokens by adding a suffix to the model name in this format:
- `anthropic:claude-3-7-sonnet-20250219:1k` - Use 1024 thinking tokens
- `anthropic:claude-3-7-sonnet-20250219:4k` - Use 4096 thinking tokens
- `anthropic:claude-3-7-sonnet-20250219:8000` - Use 8000 thinking tokens

Notes:
- Thinking tokens are only supported for the `claude-3-7-sonnet-20250219` model
- Valid thinking token budgets range from 1024 to 16000
- Values outside this range will be automatically adjusted to be within range
- You can specify the budget with k notation (1k, 4k, etc.) or with exact numbers (1024, 4096, etc.)

# Thinking Budget with Gemini

The Google Gemini model `gemini-2.5-flash-preview-04-17` supports extended thinking capabilities using thinking budget. This allows Gemini to perform more thorough reasoning before providing a response.

You can enable thinking budget by adding a suffix to the model name in this format:
- `gemini:gemini-2.5-flash-preview-04-17:1k` - Use 1024 thinking budget
- `gemini:gemini-2.5-flash-preview-04-17:4k` - Use 4096 thinking budget
- `gemini:gemini-2.5-flash-preview-04-17:8000` - Use 8000 thinking budget

Notes:
- Thinking budget is only supported for the `gemini-2.5-flash-preview-04-17` model
- Valid thinking budget range from 0 to 24576
- Values outside this range will be automatically adjusted to be within range
- You can specify the budget with k notation (1k, 4k, etc.) or with exact numbers (1024, 4096, etc.)

## Resources
- https://docs.anthropic.com/en/api/models-list?q=list+models
- https://github.com/googleapis/python-genai
- https://platform.openai.com/docs/api-reference/models/list
- https://api-docs.deepseek.com/api/list-models
- https://github.com/ollama/ollama-python
- https://github.com/openai/openai-python

## Master AI Coding 
Learn to code with AI with foundational [Principles of AI Coding](https://agenticengineer.com/principled-ai-coding?y=jprompt)

Follow the [IndyDevDan youtube channel](https://www.youtube.com/@indydevdan) for more AI coding tips and tricks.