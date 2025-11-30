"""
Available AI models from OpenRouter
"""

# Based on OpenRouter's current model offerings
AVAILABLE_MODELS = [
    # Claude Models (Anthropic)
    {
        "id": "anthropic/claude-opus-4.5",
        "name": "Claude Opus 4.5",
        "provider": "Anthropic",
        "description": "Most capable Claude model for complex reasoning",
        "context": "200K tokens"
    },
    {
        "id": "anthropic/claude-3.7-sonnet",
        "name": "Claude 3.7 Sonnet",
        "provider": "Anthropic",
        "description": "Balanced performance and speed",
        "context": "200K tokens"
    },
    {
        "id": "anthropic/claude-3.5-sonnet",
        "name": "Claude 3.5 Sonnet",
        "provider": "Anthropic",
        "description": "Fast and efficient Claude model",
        "context": "200K tokens"
    },
    
    # Gemini Models (Google)
    {
        "id": "google/gemini-3-pro",
        "name": "Gemini 3 Pro",
        "provider": "Google",
        "description": "Flagship multimodal reasoning model",
        "context": "1M tokens"
    },
    {
        "id": "google/gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "provider": "Google",
        "description": "Advanced reasoning and coding",
        "context": "1M tokens"
    },
    {
        "id": "google/gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "provider": "Google",
        "description": "Fast and efficient Gemini model",
        "context": "1M tokens"
    },
    {
        "id": "google/gemini-flash-1.5",
        "name": "Gemini Flash 1.5",
        "provider": "Google",
        "description": "Lightweight and fast",
        "context": "1M tokens"
    },
    
    # GPT Models (OpenAI)
    {
        "id": "openai/gpt-5.1",
        "name": "GPT-5.1",
        "provider": "OpenAI",
        "description": "Latest frontier-grade reasoning model",
        "context": "128K tokens"
    },
    {
        "id": "openai/gpt-5.1-chat",
        "name": "GPT-5.1 Chat (Instant)",
        "provider": "OpenAI",
        "description": "Fast, low-latency chat optimized",
        "context": "128K tokens"
    },
    {
        "id": "openai/gpt-5",
        "name": "GPT-5",
        "provider": "OpenAI",
        "description": "Advanced reasoning and complex tasks",
        "context": "128K tokens"
    },
    {
        "id": "openai/gpt-4o",
        "name": "GPT-4o",
        "provider": "OpenAI",
        "description": "Optimized GPT-4 model",
        "context": "128K tokens"
    },
    {
        "id": "openai/gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "provider": "OpenAI",
        "description": "Faster GPT-4 variant",
        "context": "128K tokens"
    },
    
    # Grok Models (xAI)
    {
        "id": "x-ai/grok-4.1-fast",
        "name": "Grok 4.1 Fast",
        "provider": "xAI",
        "description": "Best agentic tool-calling model",
        "context": "2M tokens"
    },
    {
        "id": "x-ai/grok-4",
        "name": "Grok 4",
        "provider": "xAI",
        "description": "Latest reasoning model with vision",
        "context": "256K tokens"
    },
    {
        "id": "x-ai/grok-3",
        "name": "Grok 3",
        "provider": "xAI",
        "description": "Flagship model for enterprise use",
        "context": "256K tokens"
    },
    {
        "id": "x-ai/grok-3-mini",
        "name": "Grok 3 Mini",
        "provider": "xAI",
        "description": "Lightweight reasoning model",
        "context": "128K tokens"
    },
]


def get_models_by_provider(provider: str = None):
    """Get models filtered by provider"""
    if provider:
        return [m for m in AVAILABLE_MODELS if m["provider"] == provider]
    return AVAILABLE_MODELS


def get_model_by_id(model_id: str):
    """Get model details by ID"""
    for model in AVAILABLE_MODELS:
        if model["id"] == model_id:
            return model
    return None


def get_providers():
    """Get list of unique providers"""
    return list(set(m["provider"] for m in AVAILABLE_MODELS))
