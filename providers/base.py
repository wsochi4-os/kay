"""
Base Provider Interface for Kutti

All providers must inherit from this common interface to ensure:
- Provider-agnostic routing
- Consistent model access
- Unified authentication
- Simple plugin support
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, AsyncGenerator, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class ProviderCapability(Enum):
    """Provider capability flags"""
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    VISION = "vision"
    TOOLS = "tools"
    STREAMING = "streaming"
    FUNCTION_CALLING = "function_calling"


@dataclass
class ProviderInfo:
    """Metadata about a provider's capabilities"""
    name: str
    display_name: str
    base_url: str
    supports: Dict[ProviderCapability, bool] = field(default_factory=dict)
    default_model: str = ""
    authentication_type: str = "api_key"  # api_key, oauth, none
    api_key_env_var: Optional[str] = None
    api_key_header: str = "Authorization"
    api_key_prefix: str = "Bearer"
    
    def __post_init__(self):
        # Ensure all capabilities are set
        for cap in ProviderCapability:
            if cap not in self.supports:
                self.supports[cap] = False


@dataclass
class ModelInfo:
    """Information about a model"""
    id: str
    name: str
    provider: str
    context_length: int = 0
    max_tokens: int = 0
    description: str = ""
    pricing: Dict[str, float] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.provider}/{self.id}"


@dataclass
class ChatMessage:
    """Chat message structure"""
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            tool_calls=data.get("tool_calls")
        )


@dataclass
class ChatResponse:
    """Chat response structure"""
    content: str
    model: str
    provider: str
    finish_reason: str
    usage: Dict[str, int] = field(default_factory=dict)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "tool_calls": self.tool_calls
        }


@dataclass
class EmbeddingResponse:
    """Embedding response structure"""
    embeddings: List[List[float]]
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)


class ProviderError(Exception):
    """Base exception for provider errors"""
    def __init__(self, message: str, provider: str, status_code: Optional[int] = None):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class AuthenticationError(ProviderError):
    """Authentication failed"""
    pass


class RateLimitError(ProviderError):
    """Rate limit exceeded"""
    pass


class ModelNotFoundError(ProviderError):
    """Model not found"""
    pass


class BaseProvider(ABC):
    """
    Base provider interface that all providers must implement.
    
    This ensures:
    - Provider-agnostic routing
    - Consistent model access
    - Unified authentication
    - Simple plugin support
    """
    
    info: ProviderInfo
    
    def __init__(self):
        """Initialize the provider with its metadata"""
        self.info = self.get_info()
        self._credentials: Optional[Dict[str, str]] = None
        self._models: Optional[List[ModelInfo]] = None
        self._last_model_refresh: float = 0
        self._model_cache_ttl: float = 3600  # 1 hour cache
    
    @abstractmethod
    def get_info(self) -> ProviderInfo:
        """Get provider metadata"""
        pass
    
    @property
    def name(self) -> str:
        """Provider name"""
        return self.info.name
    
    @property
    def display_name(self) -> str:
        """Human-readable provider name"""
        return self.info.display_name
    
    @property
    def capabilities(self) -> Dict[ProviderCapability, bool]:
        """Provider capabilities"""
        return self.info.supports
    
    def has_capability(self, capability: ProviderCapability) -> bool:
        """Check if provider supports a capability"""
        return self.capabilities.get(capability, False)
    
    # Authentication methods
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with the provider.
        
        Args:
            credentials: Dictionary containing authentication credentials
                     (e.g., {"api_key": "sk-..."})
        
        Returns:
            True if authentication succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate current credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    async def refresh_token(self) -> bool:
        """
        Refresh authentication token (for OAuth providers).
        
        Returns:
            True if token refresh succeeded, False otherwise
        
        Note: Default implementation returns False. Override for OAuth providers.
        """
        return False
    
    # Model management
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """
        List available models from the provider.
        
        Returns:
            List of ModelInfo objects
        """
        pass
    
    async def get_model(self, model_id: str) -> ModelInfo:
        """
        Get information about a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            ModelInfo object
            
        Raises:
            ModelNotFoundError: If model doesn't exist
        """
        models = await self.list_models()
        for model in models:
            if model.id == model_id:
                return model
        raise ModelNotFoundError(f"Model '{model_id}' not found", self.name)
    
    @property
    def default_model(self) -> str:
        """Default model for this provider"""
        return self.info.default_model
    
    # Core operations
    @abstractmethod
    async def chat(self, 
                  messages: List[ChatMessage], 
                  model: Optional[str] = None,
                  temperature: float = 0.7,
                  max_tokens: Optional[int] = None,
                  stream: bool = False,
                  **kwargs) -> Union[ChatResponse, AsyncGenerator[ChatResponse, None]]:
        """
        Send chat messages to the provider.
        
        Args:
            messages: List of ChatMessage objects
            model: Model to use (defaults to provider's default)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ChatResponse object or async generator if streaming
            
        Raises:
            ProviderError: If the request fails
            AuthenticationError: If not authenticated
        """
        pass
    
    async def embeddings(self, 
                        input: Union[str, List[str]],
                        model: Optional[str] = None,
                        **kwargs) -> EmbeddingResponse:
        """
        Generate embeddings.
        
        Args:
            input: Text or list of texts to embed
            model: Model to use (defaults to provider's default)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            EmbeddingResponse object
            
        Raises:
            ProviderError: If the request fails
            AuthenticationError: If not authenticated
        """
        if not self.has_capability(ProviderCapability.EMBEDDINGS):
            raise ProviderError(
                f"Provider '{self.name}' does not support embeddings", 
                self.name
            )
        raise NotImplementedError(f"Embeddings not implemented for {self.name}")
    
    # Credential management
    def set_credentials(self, credentials: Dict[str, str]) -> None:
        """Set credentials for this provider"""
        self._credentials = credentials
    
    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Get current credentials"""
        return self._credentials
    
    def clear_credentials(self) -> None:
        """Clear credentials"""
        self._credentials = None
        self._models = None
    
    # Utility methods
    def get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        headers = {"Content-Type": "application/json"}
        
        if self._credentials and "api_key" in self._credentials:
            api_key = self._credentials["api_key"]
            if self.info.api_key_header and self.info.api_key_prefix:
                headers[self.info.api_key_header] = f"{self.info.api_key_prefix} {api_key}"
            else:
                headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    def get_base_url(self) -> str:
        """Get the base URL for API requests"""
        return self.info.base_url
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, authenticated={self._credentials is not None})>"
