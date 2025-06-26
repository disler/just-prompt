# Google GenAI SDK v1.22.0 Documentation

## Overview

The Google Gen AI SDK provides an interface for developers to integrate Google's generative models into their Python applications. It supports both the Gemini Developer API and Vertex AI APIs.

**Latest Version:** 1.22.0 (Released: about 23 hours ago)

## Installation

```bash
pip install google-genai
```

## Key Features

### 1. Client Creation

**For Gemini Developer API:**
```python
from google import genai
client = genai.Client(api_key='GEMINI_API_KEY')
```

**For Vertex AI:**
```python
from google import genai
client = genai.Client(
    vertexai=True, 
    project='your-project-id', 
    location='us-central1'
)
```

### 2. Model Support

The SDK supports various models including:
- **Gemini 2.0 Flash**: `gemini-2.0-flash-001`
- **Text Embedding**: `text-embedding-004`
- **Imagen 3.0**: `imagen-3.0-generate-002` (image generation)
- **Veo 2.0**: `veo-2.0-generate-001` (video generation)

### 3. Core Capabilities

#### Generate Content
```python
response = client.models.generate_content(
    model='gemini-2.0-flash-001', 
    contents='Why is the sky blue?'
)
print(response.text)
```

#### Chat Sessions
```python
chat = client.chats.create(model='gemini-2.0-flash-001')
response = chat.send_message('tell me a story')
print(response.text)
```

#### Function Calling
The SDK supports automatic Python function calling:
```python
def get_current_weather(location: str) -> str:
    """Returns the current weather."""
    return 'sunny'

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)
```

#### JSON Response Schema
Supports Pydantic models for structured output:
```python
from pydantic import BaseModel

class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=CountryInfo,
    ),
)
```

### 4. Advanced Features

#### Streaming Support
```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.0-flash-001', 
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

#### Async Support
```python
response = await client.aio.models.generate_content(
    model='gemini-2.0-flash-001', 
    contents='Tell me a story in 300 words.'
)
```

#### Caching
```python
cached_content = client.caches.create(
    model='gemini-2.0-flash-001',
    config=types.CreateCachedContentConfig(
        contents=[...],
        system_instruction='What is the sum of the two pdfs?',
        display_name='test cache',
        ttl='3600s',
    ),
)
```

#### Fine-tuning
Supports supervised fine-tuning with different approaches for Vertex AI (GCS) and Gemini Developer API (inline examples).

### 5. API Configuration

#### API Version Selection
```python
from google.genai import types

# For stable API endpoints
client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1',
    http_options=types.HttpOptions(api_version='v1')
)
```

#### Proxy Support
```bash
export HTTPS_PROXY='http://username:password@proxy_uri:port'
export SSL_CERT_FILE='client.pem'
```

### 6. Error Handling

```python
from google.genai import errors

try:
    client.models.generate_content(
        model="invalid-model-name",
        contents="What is your name?",
    )
except errors.APIError as e:
    print(e.code)  # 404
    print(e.message)
```

## Platform Support

- **Python Version:** >=3.9
- **Supported Python Versions:** 3.9, 3.10, 3.11, 3.12, 3.13
- **License:** Apache Software License (Apache-2.0)
- **Operating System:** OS Independent

## Additional Resources

- **Homepage:** https://github.com/googleapis/python-genai
- **Documentation:** https://googleapis.github.io/python-genai/
- **PyPI Page:** https://pypi.org/project/google-genai/

## Recent Updates

The v1.22.0 release continues to support the latest Gemini models and maintains compatibility with both Gemini Developer API and Vertex AI platforms. The SDK provides comprehensive support for generative AI tasks including text generation, image generation, video generation, embeddings, and more.