# Google GenAI API Update

## PyPI Package Information

### Latest Version
- Package: google-genai
- Latest version: 1.22.0 (current installed: 1.11.0)
- Summary: GenAI Python SDK
- Documentation: https://googleapis.github.io/python-genai/

### Dependencies
```json
{
  "anyio": ">=4.8.0,<5.0.0",
  "google-auth": ">=2.14.1,<3.0.0",
  "httpx": ">=0.28.1,<1.0.0",
  "pydantic": ">=2.0.0,<3.0.0",
  "requests": ">=2.28.1,<3.0.0",
  "tenacity": ">=8.2.3,<9.0.0",
  "websockets": ">=13.0.0,<15.1.0",
  "typing-extensions": ">=4.11.0,<5.0.0"
}
```

### Recent Versions
- 1.22.0 (latest)
- 1.21.1
- 1.21.0
- 1.20.0
- 1.19.0
- 1.18.0
- 1.17.0
- 1.16.1
- 1.16.0
- 1.15.0

## Correct API Usage

The correct way to list models using the google-genai library is:

```python
from google import genai

# Initialize client
client = genai.Client(api_key="your-api-key")

# List models
models = client.models.list()
model_list = []
for model in models:
    model_list.append(model.name)
```

### Key API Examples from Documentation

1. **List Models**:
```python
for model in client.models.list():
    print(model)
```

2. **Generate Content**:
```python
response = client.models.generate_content(
    model='gemini-2.0-flash-001', 
    contents='Why is the sky blue?'
)
print(response.text)
```

3. **With Config**:
```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='high',
    config=types.GenerateContentConfig(
        system_instruction='I say high, you say low',
        max_output_tokens=3,
        temperature=0.3,
    ),
)
```

## Available Gemini 2.5 Pro Models

As of the latest API call, the following Gemini 2.5 Pro models are available:
- models/gemini-2.5-pro
- models/gemini-2.5-pro-preview-03-25
- models/gemini-2.5-pro-preview-05-06
- models/gemini-2.5-pro-preview-06-05
- models/gemini-2.5-pro-preview-tts

## Key Changes
1. Use `client.models.list()` instead of `client.list_models()`
2. The method returns an iterator of model objects
3. Models are prefixed with "models/" in the API response
4. Total models available: 58 (including various Gemini versions)
5. Library version should be updated from 1.11.0 to 1.22.0