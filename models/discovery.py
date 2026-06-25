"""
Model Discovery

Dynamic model discovery and metadata management.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
import aiohttp

from providers.base import BaseProvider, ModelInfo, ProviderError
from providers.registry import registry
from .registry import model_registry


@dataclass
class ModelDiscovery:
    """
    Model Discovery
    
    Handles dynamic discovery of models from various sources.
    """
    known_model_sources: Dict[str, str] = field(default_factory=dict)
    custom_models: Dict[str, ModelInfo] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize known model sources"""
        # Known model sources (provider -> API endpoint)
        self.known_model_sources = {
            "openai": "https://api.openai.com/v1/models",
            "anthropic": "https://api.anthropic.com/v1/models",
            "groq": "https://api.groq.com/openai/v1/models",
            "openrouter": "https://openrouter.ai/api/v1/models",
            "mistral": "https://api.mistral.ai/v1/models",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
            "fireworks": "https://api.fireworks.ai/inference/v1/models",
            "together": "https://api.together.xyz/v1/models",
            "deepseek": "https://api.deepseek.com/v1/models",
        }
    
    async def discover_from_provider(self, provider_name: str) -> List[ModelInfo]:
        """
        Discover models from a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of ModelInfo objects
        """
        provider = registry.get(provider_name)
        if not provider:
            return []
        
        try:
            return await provider.list_models()
        except Exception:
            return []
    
    async def discover_all(self) -> Dict[str, List[ModelInfo]]:
        """
        Discover models from all providers.
        
        Returns:
            Dictionary mapping provider names to lists of ModelInfo
        """
        results = {}
        
        for provider_name in registry.list():
            models = await self.discover_from_provider(provider_name)
            if models:
                results[provider_name] = models
        
        return results
    
    async def discover_from_api(self, provider_name: str, api_url: str, api_key: Optional[str] = None) -> List[ModelInfo]:
        """
        Discover models from a provider's API directly.
        
        Args:
            provider_name: Name of the provider
            api_url: URL of the models endpoint
            api_key: Optional API key for authentication
            
        Returns:
            List of ModelInfo objects
        """
        models = []
        
        try:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Handle different API response formats
                        if "data" in data:
                            # OpenAI-style response
                            for model_data in data["data"]:
                                models.append(ModelInfo(
                                    id=model_data.get("id", ""),
                                    name=model_data.get("id", ""),
                                    provider=provider_name,
                                    context_length=model_data.get("context_length", 0),
                                    description=model_data.get("description", "")
                                ))
                        elif "models" in data:
                            # Some other format
                            for model_data in data["models"]:
                                models.append(ModelInfo(
                                    id=model_data.get("id", ""),
                                    name=model_data.get("name", ""),
                                    provider=provider_name,
                                    context_length=model_data.get("context_length", 0)
                                ))
                        else:
                            # Try to extract models from any list
                            for item in data.values():
                                if isinstance(item, list):
                                    for model_data in item:
                                        if isinstance(model_data, dict) and "id" in model_data:
                                            models.append(ModelInfo(
                                                id=model_data.get("id", ""),
                                                name=model_data.get("name", model_data.get("id", "")),
                                                provider=provider_name
                                            ))
        except Exception:
            pass
        
        return models
    
    def add_custom_model(self, model_info: ModelInfo) -> None:
        """
        Add a custom model definition.
        
        Args:
            model_info: ModelInfo object for the custom model
        """
        self.custom_models[model_info.id] = model_info
        model_registry.models[model_info.id] = model_info
        
        if model_info.provider not in model_registry.provider_models:
            model_registry.provider_models[model_info.provider] = []
        
        # Remove old version if exists
        model_registry.provider_models[model_info.provider] = [
            m for m in model_registry.provider_models[model_info.provider] 
            if m.id != model_info.id
        ]
        model_registry.provider_models[model_info.provider].append(model_info)
    
    def remove_custom_model(self, model_id: str) -> bool:
        """
        Remove a custom model.
        
        Args:
            model_id: ID of the model to remove
            
        Returns:
            True if model was removed, False otherwise
        """
        if model_id in self.custom_models:
            model = self.custom_models[model_id]
            del self.custom_models[model_id]
            
            if model_id in model_registry.models:
                del model_registry.models[model_id]
            
            if model.provider in model_registry.provider_models:
                model_registry.provider_models[model.provider] = [
                    m for m in model_registry.provider_models[model.provider] 
                    if m.id != model_id
                ]
            
            return True
        return False
    
    def list_custom_models(self) -> List[ModelInfo]:
        """
        List all custom models.
        
        Returns:
            List of custom ModelInfo objects
        """
        return list(self.custom_models.values())
    
    def get_model_source(self, provider_name: str) -> Optional[str]:
        """
        Get the model source URL for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            URL of the models endpoint, or None if not known
        """
        return self.known_model_sources.get(provider_name)
    
    def add_model_source(self, provider_name: str, api_url: str) -> None:
        """
        Add a custom model source.
        
        Args:
            provider_name: Name of the provider
            api_url: URL of the models endpoint
        """
        self.known_model_sources[provider_name] = api_url
    
    async def sync_with_registry(self) -> int:
        """
        Synchronize custom models with the global registry.
        
        Returns:
            Number of models synchronized
        """
        count = 0
        
        for model in self.custom_models.values():
            if model.id not in model_registry.models:
                model_registry.models[model.id] = model
                count += 1
        
        return count
    
    def __repr__(self) -> str:
        return f"<ModelDiscovery custom_models={len(self.custom_models)} sources={len(self.known_model_sources)}>"


# Global model discovery instance
model_discovery = ModelDiscovery()
