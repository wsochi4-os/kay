"""
OpenAI Provider Implementation

Supports:
- Chat completions
- Embeddings
- Model listing
- Tool calling
- Function calling
"""

import aiohttp
import json
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
import asyncio

from .base import (
    BaseProvider, 
    ProviderInfo, 
    ProviderCapability,
    ModelInfo,
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
    AuthenticationError,
    ProviderError
)


class OpenAIProvider(BaseProvider):
    """OpenAI API provider"""
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="openai",
            display_name="OpenAI",
            base_url="https://api.openai.com/v1",
            supports={
                ProviderCapability.CHAT: True,
                ProviderCapability.EMBEDDINGS: True,
                ProviderCapability.VISION: True,
                ProviderCapability.TOOLS: True,
                ProviderCapability.STREAMING: True,
                ProviderCapability.FUNCTION_CALLING: True,
            },
            default_model="gpt-4o",
            authentication_type="api_key",
            api_key_env_var="OPENAI_API_KEY",
            api_key_header="Authorization",
            api_key_prefix="Bearer"
        )
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with OpenAI API key"""
        if not credentials or "api_key" not in credentials:
            return False
        
        self.set_credentials(credentials)
        return await self.validate_credentials()
    
    async def validate_credentials(self) -> bool:
        """Validate OpenAI credentials by listing models"""
        if not self._credentials or "api_key" not in self._credentials:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/models"
                headers = self.get_headers()
                
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        self.clear_credentials()
                        return False
                    else:
                        return False
        except Exception:
            return False
    
    async def list_models(self) -> List[ModelInfo]:
        """List available OpenAI models"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/models"
                headers = self.get_headers()
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = []
                        for model_data in data.get("data", []):
                            model_id = model_data.get("id", "")
                            if model_id.startswith("gpt-") or model_id.startswith("text-"):
                                models.append(ModelInfo(
                                    id=model_id,
                                    name=model_data.get("id", ""),
                                    provider=self.name,
                                    context_length=model_data.get("context_length", 0),
                                    description=model_data.get("description", ""),
                                    capabilities=["chat"]
                                ))
                        return models
                    else:
                        raise ProviderError(f"Failed to list models: {response.status}", self.name)
        except Exception as e:
            raise ProviderError(f"Failed to list models: {str(e)}", self.name)
    
    async def chat(self,
                  messages: List[ChatMessage],
                  model: Optional[str] = None,
                  temperature: float = 0.7,
                  max_tokens: Optional[int] = None,
                  stream: bool = False,
                  **kwargs) -> Union[ChatResponse, AsyncGenerator[ChatResponse, None]]:
        """Send chat messages to OpenAI"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or self.default_model
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_msg = {"role": msg.role, "content": msg.content}
            if msg.name:
                openai_msg["name"] = msg.name
            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls
            openai_messages.append(openai_msg)
        
        payload = {
            "model": model,
            "messages": openai_messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Add tool support if available
        if kwargs.get("tools"):
            payload["tools"] = kwargs["tools"]
        if kwargs.get("tool_choice"):
            payload["tool_choice"] = kwargs["tool_choice"]
        
        if stream:
            return self._chat_stream(payload)
        else:
            return await self._chat_single(payload)
    
    async def _chat_single(self, payload: Dict[str, Any]) -> ChatResponse:
        """Single chat completion (non-streaming)"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/chat/completions"
                headers = self.get_headers()
                
                async with session.post(url, json=payload, headers=headers, timeout=120) as response:
                    if response.status == 200:
                        data = await response.json()
                        choice = data.get("choices", [{}])[0]
                        message = choice.get("message", {})
                        
                        return ChatResponse(
                            content=message.get("content", ""),
                            model=data.get("model", self.default_model),
                            provider=self.name,
                            finish_reason=choice.get("finish_reason", "unknown"),
                            usage=data.get("usage", {}),
                            tool_calls=message.get("tool_calls")
                        )
                    elif response.status == 401:
                        self.clear_credentials()
                        raise AuthenticationError("Invalid API key", self.name)
                    elif response.status == 404:
                        raise ProviderError(f"Model not found", self.name, 404)
                    else:
                        error_data = await response.text()
                        raise ProviderError(f"API error: {error_data}", self.name, response.status)
        except Exception as e:
            raise ProviderError(f"Chat request failed: {str(e)}", self.name)
    
    async def _chat_stream(self, payload: Dict[str, Any]) -> AsyncGenerator[ChatResponse, None]:
        """Streaming chat completion"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/chat/completions"
                headers = self.get_headers()
                
                async with session.post(url, json=payload, headers=headers, timeout=120) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    data_str = line_str[6:]
                                    if data_str != '[DONE]':
                                        try:
                                            data = json.loads(data_str)
                                            choice = data.get("choices", [{}])[0]
                                            if choice and "delta" in choice:
                                                delta = choice["delta"]
                                                content = delta.get("content", "")
                                                if content:
                                                    yield ChatResponse(
                                                        content=content,
                                                        model=data.get("model", self.default_model),
                                                        provider=self.name,
                                                        finish_reason="streaming"
                                                    )
                                        except json.JSONDecodeError:
                                            continue
                    elif response.status == 401:
                        self.clear_credentials()
                        raise AuthenticationError("Invalid API key", self.name)
                    else:
                        error_data = await response.text()
                        raise ProviderError(f"API error: {error_data}", self.name, response.status)
        except Exception as e:
            raise ProviderError(f"Streaming failed: {str(e)}", self.name)
    
    async def embeddings(self,
                        input: Union[str, List[str]],
                        model: Optional[str] = None,
                        **kwargs) -> EmbeddingResponse:
        """Generate embeddings with OpenAI"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or "text-embedding-3-small"
        
        if isinstance(input, str):
            input = [input]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/embeddings"
                headers = self.get_headers()
                
                payload = {
                    "model": model,
                    "input": input,
                    "encoding_format": "float"
                }
                
                async with session.post(url, json=payload, headers=headers, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        return EmbeddingResponse(
                            embeddings=data.get("data", []),
                            model=data.get("model", model),
                            provider=self.name,
                            usage=data.get("usage", {})
                        )
                    elif response.status == 401:
                        self.clear_credentials()
                        raise AuthenticationError("Invalid API key", self.name)
                    else:
                        error_data = await response.text()
                        raise ProviderError(f"API error: {error_data}", self.name, response.status)
        except Exception as e:
            raise ProviderError(f"Embedding request failed: {str(e)}", self.name)


# Singleton instance
openai_provider = OpenAIProvider()
