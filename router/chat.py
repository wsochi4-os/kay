"""
Unified Request Router

Resolves provider, loads credentials, validates session, selects model, dispatches requests.

Consumers should never call providers directly.
All requests must pass through the router layer.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass, field
import asyncio

from providers.base import (
    BaseProvider, 
    ChatMessage, 
    ChatResponse, 
    EmbeddingResponse,
    ProviderError,
    AuthenticationError
)
from providers.registry import registry
from auth.manager import auth_manager
from models.registry import model_registry


@dataclass
class RouterConfig:
    """Configuration for the router"""
    default_provider: str = "groq"
    default_model: str = "llama-3.3-70b-versatile"
    timeout: float = 120.0
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class ChatRequest:
    """Chat request structure"""
    messages: List[ChatMessage]
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "messages": [m.to_dict() for m in self.messages],
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream,
            "tools": self.tools,
            "tool_choice": self.tool_choice,
            "extra_headers": self.extra_headers
        }


class ChatRouter:
    """
    Unified Request Router
    
    Responsibilities:
    - Resolve provider
    - Load credentials
    - Validate session
    - Select model
    - Dispatch requests
    - Handle provider-specific normalization
    """
    
    def __init__(self, config: Optional[RouterConfig] = None):
        """
        Initialize the chat router.
        
        Args:
            config: Router configuration
        """
        self.config = config or RouterConfig()
    
    async def chat(self, 
                   messages: List[ChatMessage],
                   provider: Optional[str] = None,
                   model: Optional[str] = None,
                   temperature: float = 0.7,
                   max_tokens: Optional[int] = None,
                   stream: bool = False,
                   **kwargs) -> Union[ChatResponse, AsyncGenerator[ChatResponse, None]]:
        """
        Send a chat request through the router.
        
        Args:
            messages: List of ChatMessage objects
            provider: Provider to use (None for active provider)
            model: Model to use (None for provider default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ChatResponse object or async generator if streaming
            
        Raises:
            ProviderError: If the request fails
            AuthenticationError: If not authenticated
        """
        # Resolve provider
        resolved_provider = self._resolve_provider(provider)
        if not resolved_provider:
            raise ProviderError(f"No provider available: {provider}", "router")
        
        # Load credentials
        provider_instance = await self._load_provider_credentials(resolved_provider)
        if not provider_instance:
            raise AuthenticationError(f"Not authenticated with {resolved_provider}", "router")
        
        # Resolve model
        resolved_model = self._resolve_model(model, resolved_provider, provider_instance)
        
        # Dispatch request
        try:
            return await provider_instance.chat(
                messages=messages,
                model=resolved_model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
        except ProviderError as e:
            raise ProviderError(f"Provider error: {e.message}", resolved_provider)
        except AuthenticationError as e:
            raise AuthenticationError(f"Authentication error: {e.message}", resolved_provider)
    
    async def embeddings(self,
                        input: Union[str, List[str]],
                        provider: Optional[str] = None,
                        model: Optional[str] = None,
                        **kwargs) -> EmbeddingResponse:
        """
        Generate embeddings through the router.
        
        Args:
            input: Text or list of texts to embed
            provider: Provider to use (None for active provider)
            model: Model to use (None for provider default)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            EmbeddingResponse object
            
        Raises:
            ProviderError: If the request fails
            AuthenticationError: If not authenticated
        """
        # Resolve provider
        resolved_provider = self._resolve_provider(provider)
        if not resolved_provider:
            raise ProviderError(f"No provider available: {provider}", "router")
        
        # Load credentials
        provider_instance = await self._load_provider_credentials(resolved_provider)
        if not provider_instance:
            raise AuthenticationError(f"Not authenticated with {resolved_provider}", "router")
        
        # Resolve model
        resolved_model = self._resolve_model(model, resolved_provider, provider_instance)
        
        # Dispatch request
        try:
            return await provider_instance.embeddings(
                input=input,
                model=resolved_model,
                **kwargs
            )
        except ProviderError as e:
            raise ProviderError(f"Provider error: {e.message}", resolved_provider)
        except AuthenticationError as e:
            raise AuthenticationError(f"Authentication error: {e.message}", resolved_provider)
    
    def _resolve_provider(self, provider: Optional[str]) -> str:
        """
        Resolve the provider to use.
        
        Args:
            provider: Provider name (None for active provider)
            
        Returns:
            Resolved provider name
        """
        if provider:
            return provider
        
        # Use active provider from auth manager
        active = auth_manager.get_active_provider()
        if active:
            return active
        
        # Fall back to default
        return self.config.default_provider
    
    async def _load_provider_credentials(self, provider_name: str) -> Optional[BaseProvider]:
        """
        Load a provider instance with credentials.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider instance with credentials loaded, or None if not authenticated
        """
        # Get provider from registry
        provider = registry.get(provider_name)
        if not provider:
            return None
        
        # Try to get credentials from auth manager
        authenticated = auth_manager.is_authenticated(provider_name)
        if not authenticated:
            # Try environment variable
            env_var = provider.info.api_key_env_var
            if env_var and env_var in os.environ:
                provider.set_credentials({"api_key": os.environ[env_var]})
                return provider
            
            return None
        
        # Get provider with credentials from auth manager
        return await auth_manager.get_provider(provider_name)
    
    def _resolve_model(self, 
                       model: Optional[str], 
                       provider_name: str,
                       provider: BaseProvider) -> str:
        """
        Resolve the model to use.
        
        Args:
            model: Model name (None for provider default)
            provider_name: Name of the provider
            provider: Provider instance
            
        Returns:
            Resolved model name
        """
        if model:
            return model
        
        # Try to get from model registry
        active_session = auth_manager.get_active_session()
        if active_session and active_session.get("model"):
            return active_session["model"]
        
        # Use provider default
        return provider.default_model
    
    def list_providers(self) -> List[str]:
        """
        List all available providers.
        
        Returns:
            List of provider names
        """
        return registry.list()
    
    def list_authenticated_providers(self) -> List[str]:
        """
        List all authenticated providers.
        
        Returns:
            List of authenticated provider names
        """
        return auth_manager.list_authenticated_providers()
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider information dictionary
        """
        return auth_manager.get_provider_info(provider_name)
    
    def set_default_provider(self, provider_name: str) -> None:
        """
        Set the default provider.
        
        Args:
            provider_name: Name of the provider
        """
        self.config.default_provider = provider_name
    
    def set_default_model(self, model: str) -> None:
        """
        Set the default model.
        
        Args:
            model: Model name
        """
        self.config.default_model = model
    
    def __repr__(self) -> str:
        return f"<ChatRouter default_provider={self.config.default_provider} default_model={self.config.default_model}>"


# Global router instance
router = ChatRouter()


# Convenience functions
async def chat(
    messages: List[ChatMessage],
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs
) -> Union[ChatResponse, AsyncGenerator[ChatResponse, None]]:
    """Send a chat request through the router"""
    return await router.chat(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
        **kwargs
    )


async def embeddings(
    input: Union[str, List[str]],
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> EmbeddingResponse:
    """Generate embeddings through the router"""
    return await router.embeddings(
        input=input,
        provider=provider,
        model=model,
        **kwargs
    )
