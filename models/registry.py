"""
Model Registry

Manages model information and discovery across all providers.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import asyncio

from providers.base import BaseProvider, ModelInfo, ProviderError
from providers.registry import registry


@dataclass
class ModelRegistry:
    """
    Model Registry
    
    Manages model information and discovery across all providers.
    """
    models: Dict[str, ModelInfo] = field(default_factory=dict)  # model_id -> ModelInfo
    provider_models: Dict[str, List[ModelInfo]] = field(default_factory=dict)  # provider_name -> List[ModelInfo]
    last_refresh: float = 0
    cache_ttl: float = 3600  # 1 hour
    storage_path: Path = field(default_factory=lambda: Path.home() / ".kutti" / "models.json")
    
    def __post_init__(self):
        """Load models from cache"""
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load models from cache file"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.last_refresh = data.get("last_refresh", 0)
                    
                    for model_id, model_data in data.get("models", {}).items():
                        try:
                            model = ModelInfo(**model_data)
                            self.models[model_id] = model
                        except Exception:
                            continue
                    
                    for provider_name, model_list in data.get("provider_models", {}).items():
                        try:
                            models = [ModelInfo(**m) for m in model_list]
                            self.provider_models[provider_name] = models
                        except Exception:
                            continue
        except Exception:
            self.models = {}
            self.provider_models = {}
            self.last_refresh = 0
    
    def _save_cache(self) -> None:
        """Save models to cache file"""
        try:
            data = {
                "last_refresh": self.last_refresh,
                "models": {mid: model.__dict__ for mid, model in self.models.items()},
                "provider_models": {
                    pname: [model.__dict__ for model in models]
                    for pname, models in self.provider_models.items()
                }
            }
            
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(self.storage_path, 0o600)
        except Exception:
            pass
    
    async def refresh(self, force: bool = False) -> int:
        """
        Refresh model information from all providers.
        
        Args:
            force: Force refresh even if cache is still valid
            
        Returns:
            Number of models refreshed
        """
        # Check if refresh is needed
        if not force and (time.time() - self.last_refresh) < self.cache_ttl:
            return 0
        
        count = 0
        self.models.clear()
        self.provider_models.clear()
        
        # Refresh from all providers
        for provider_name in registry.list():
            provider = registry.get(provider_name)
            if provider:
                try:
                    models = await provider.list_models()
                    for model in models:
                        self.models[model.id] = model
                        if provider_name not in self.provider_models:
                            self.provider_models[provider_name] = []
                        self.provider_models[provider_name].append(model)
                        count += 1
                except Exception:
                    continue
        
        self.last_refresh = time.time()
        self._save_cache()
        
        return count
    
    async def refresh_provider(self, provider_name: str) -> int:
        """
        Refresh model information from a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Number of models refreshed
        """
        provider = registry.get(provider_name)
        if not provider:
            return 0
        
        count = 0
        
        try:
            models = await provider.list_models()
            for model in models:
                self.models[model.id] = model
                if provider_name not in self.provider_models:
                    self.provider_models[provider_name] = []
                
                # Remove old models from this provider
                self.provider_models[provider_name] = [
                    m for m in self.provider_models[provider_name] 
                    if m.id != model.id
                ]
                self.provider_models[provider_name].append(model)
                count += 1
        except Exception:
            pass
        
        self._save_cache()
        return count
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get information about a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            ModelInfo object, or None if not found
        """
        return self.models.get(model_id)
    
    def get_models_by_provider(self, provider_name: str) -> List[ModelInfo]:
        """
        Get all models from a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of ModelInfo objects
        """
        return self.provider_models.get(provider_name, [])
    
    def list_all_models(self) -> List[ModelInfo]:
        """
        List all known models.
        
        Returns:
            List of all ModelInfo objects
        """
        return list(self.models.values())
    
    def list_model_ids(self) -> List[str]:
        """
        List all known model IDs.
        
        Returns:
            List of model IDs
        """
        return list(self.models.keys())
    
    def search_models(self, query: str) -> List[ModelInfo]:
        """
        Search for models by name or ID.
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching ModelInfo objects
        """
        query = query.lower()
        results = []
        
        for model in self.models.values():
            if (query in model.id.lower() or 
                query in model.name.lower() or 
                query in model.provider.lower()):
                results.append(model)
        
        return results
    
    def get_provider_for_model(self, model_id: str) -> Optional[str]:
        """
        Get the provider that offers a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            Provider name, or None if not found
        """
        model = self.get_model(model_id)
        if model:
            return model.provider
        return None
    
    def get_models_by_capability(self, capability: str) -> List[ModelInfo]:
        """
        Get all models that support a specific capability.
        
        Args:
            capability: The capability to filter by
            
        Returns:
            List of ModelInfo objects
        """
        results = []
        for model in self.models.values():
            if capability in model.capabilities:
                results.append(model)
        return results
    
    def is_cache_valid(self) -> bool:
        """
        Check if the model cache is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        return (time.time() - self.last_refresh) < self.cache_ttl
    
    def clear_cache(self) -> None:
        """Clear the model cache"""
        self.models.clear()
        self.provider_models.clear()
        self.last_refresh = 0
        
        # Remove cache file
        try:
            if self.storage_path.exists():
                self.storage_path.unlink()
        except Exception:
            pass
    
    def __len__(self) -> int:
        """Number of known models"""
        return len(self.models)
    
    def __repr__(self) -> str:
        return f"<ModelRegistry with {len(self)} models from {len(self.provider_models)} providers>"


# Global model registry instance
model_registry = ModelRegistry()


# Convenience functions
async def refresh_models(force: bool = False) -> int:
    """Refresh all models"""
    return await model_registry.refresh(force)


def get_model(model_id: str) -> Optional[ModelInfo]:
    """Get a model by ID"""
    return model_registry.get_model(model_id)


def list_models() -> List[ModelInfo]:
    """List all models"""
    return model_registry.list_all_models()
