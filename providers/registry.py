"""
Provider Registry

Dynamic provider discovery and registration.

Purpose:
- Dynamic provider discovery and registration
- Providers should self-register automatically
- Support for plugin providers
"""

from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, field
import importlib
import pkgutil
import sys
from pathlib import Path

from .base import BaseProvider, ProviderInfo, ProviderCapability, ModelInfo


@dataclass
class ProviderRegistry:
    """Registry for all available providers"""
    providers: Dict[str, BaseProvider] = field(default_factory=dict)
    provider_classes: Dict[str, Type[BaseProvider]] = field(default_factory=dict)
    
    def register(self, provider: BaseProvider) -> None:
        """Register a provider instance"""
        self.providers[provider.name] = provider
        self.provider_classes[provider.name] = provider.__class__
    
    def register_class(self, provider_class: Type[BaseProvider]) -> None:
        """Register a provider class (creates instance)"""
        provider = provider_class()
        self.register(provider)
    
    def get(self, name: str) -> Optional[BaseProvider]:
        """Get a provider by name"""
        return self.providers.get(name)
    
    def get_class(self, name: str) -> Optional[Type[BaseProvider]]:
        """Get a provider class by name"""
        return self.provider_classes.get(name)
    
    def list(self) -> List[str]:
        """List all registered provider names"""
        return list(self.providers.keys())
    
    def list_providers(self) -> List[BaseProvider]:
        """List all registered provider instances"""
        return list(self.providers.values())
    
    def list_info(self) -> List[ProviderInfo]:
        """List all provider metadata"""
        return [p.info for p in self.providers.values()]
    
    def unregister(self, name: str) -> bool:
        """Unregister a provider"""
        if name in self.providers:
            del self.providers[name]
            if name in self.provider_classes:
                del self.provider_classes[name]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered providers"""
        self.providers.clear()
        self.provider_classes.clear()
    
    def discover_providers(self, package: str = "providers") -> int:
        """
        Discover and register all providers in a package.
        
        Args:
            package: Python package name to search for providers
            
        Returns:
            Number of providers discovered and registered
        """
        count = 0
        
        try:
            # Import the package
            package_module = importlib.import_module(package)
            package_path = Path(package_module.__file__).parent
            
            # Iterate through all modules in the package
            for finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
                if not name.startswith("_"):
                    try:
                        module = importlib.import_module(f"{package}.{name}")
                        
                        # Look for provider instances or classes
                        for attr_name in dir(module):
                            if not attr_name.startswith("_"):
                                attr = getattr(module, attr_name)
                                
                                # Check if it's a provider instance
                                if isinstance(attr, BaseProvider):
                                    self.register(attr)
                                    count += 1
                                
                                # Check if it's a provider class
                                elif (isinstance(attr, type) and 
                                      issubclass(attr, BaseProvider) and 
                                      attr is not BaseProvider):
                                    self.register_class(attr)
                                    count += 1
                    except Exception as e:
                        # Skip modules that can't be imported
                        continue
        except Exception as e:
            # Package doesn't exist or can't be imported
            pass
        
        return count
    
    def load_plugin_provider(self, module_path: str) -> bool:
        """
        Load a provider from a plugin module.
        
        Args:
            module_path: Path to the Python module containing the provider
            
        Returns:
            True if provider was loaded successfully
        """
        try:
            # Get the module name from path
            spec = importlib.util.spec_from_file_location("plugin_provider", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["plugin_provider"] = module
                spec.loader.exec_module(module)
                
                # Look for provider instances or classes
                for attr_name in dir(module):
                    if not attr_name.startswith("_"):
                        attr = getattr(module, attr_name)
                        
                        if isinstance(attr, BaseProvider):
                            self.register(attr)
                            return True
                        
                        elif (isinstance(attr, type) and 
                              issubclass(attr, BaseProvider) and 
                              attr is not BaseProvider):
                            self.register_class(attr)
                            return True
        except Exception as e:
            return False
        
        return False
    
    def get_provider_by_model(self, model_id: str) -> Optional[BaseProvider]:
        """
        Get the provider that supports a specific model.
        
        Args:
            model_id: The model identifier (e.g., "gpt-4", "claude-3-sonnet")
            
        Returns:
            Provider that supports the model, or None if not found
        """
        for provider in self.providers.values():
            try:
                # Check if this provider has the model
                models = provider.list_models()
                if isinstance(models, list):
                    for model in models:
                        if model.id == model_id:
                            return provider
            except Exception:
                continue
        return None
    
    def get_providers_by_capability(self, capability: ProviderCapability) -> List[BaseProvider]:
        """
        Get all providers that support a specific capability.
        
        Args:
            capability: The capability to filter by
            
        Returns:
            List of providers supporting the capability
        """
        return [
            p for p in self.providers.values() 
            if p.has_capability(capability)
        ]
    
    def __contains__(self, name: str) -> bool:
        """Check if a provider is registered"""
        return name in self.providers
    
    def __len__(self) -> int:
        """Number of registered providers"""
        return len(self.providers)
    
    def __repr__(self) -> str:
        return f"<ProviderRegistry with {len(self)} providers>"


# Global registry instance
registry = ProviderRegistry()


# Auto-discover and register built-in providers
def _initialize_registry():
    """Initialize the registry with built-in providers"""
    # Import all provider modules to trigger registration
    from . import openai, anthropic, groq, openrouter, mistral
    from . import gemini, fireworks, together, deepseek
    
    # Register all provider instances
    registry.register(openai.openai_provider)
    registry.register(anthropic.anthropic_provider)
    registry.register(groq.groq_provider)
    registry.register(openrouter.openrouter_provider)
    registry.register(mistral.mistral_provider)
    registry.register(gemini.gemini_provider)
    registry.register(fireworks.fireworks_provider)
    registry.register(together.together_provider)
    registry.register(deepseek.deepseek_provider)


# Initialize on import
_initialize_registry()
