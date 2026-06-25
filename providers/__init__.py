# Providers package
# Import all providers to ensure they're registered

from .base import BaseProvider, ProviderInfo, ProviderCapability
from .registry import registry

# Import all provider instances to trigger registration
from .openai import openai_provider
from .anthropic import anthropic_provider
from .groq import groq_provider
from .openrouter import openrouter_provider
from .mistral import mistral_provider
from .gemini import gemini_provider
from .fireworks import fireworks_provider
from .together import together_provider
from .deepseek import deepseek_provider

__all__ = [
    "BaseProvider",
    "ProviderInfo", 
    "ProviderCapability",
    "registry",
    "openai_provider",
    "anthropic_provider",
    "groq_provider",
    "openrouter_provider",
    "mistral_provider",
    "gemini_provider",
    "fireworks_provider",
    "together_provider", 
    "deepseek_provider",
]