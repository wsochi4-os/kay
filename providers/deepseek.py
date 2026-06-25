"""
DeepSeek Provider Implementation

Supports:
- Chat completions
- Model listing
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


class DeepSeekProvider(BaseProvider):
    """DeepSeek API provider"""
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="deepseek",
            display_name="DeepSeek",
            base_url="https://api.deepseek.com/v1",
            supports={
                ProviderCapability.CHAT: True,
                ProviderCapability.EMBEDDINGS: False,
                ProviderCapability.VISION: False,
                ProviderCapability.TOOLS: False,
                ProviderCapability.STREAMING: True,
                ProviderCapability.FUNCTION_CALLING: False,
            },
            default_model="deepseek-chat",
            authentication_type="api_key",
            api_key_env_var="DEEPSEEK_API_KEY",
            api_key_header="Authorization",
            api_key_prefix="Bearer"
        )
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with DeepSeek API key"""
        if not credentials or "api_key" not in credentials:
            return False
        
        self.set_credentials(credentials)
        return await self.validate_credentials()
    
    async def validate_credentials(self) -> bool:
        """Validate DeepSeek credentials by making a test request"""
        if not self._credentials or "api_key" not in self._credentials:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use a simple chat completion to validate
                url = f"{self.get_base_url()}/chat/completions"
                headers = self.get_headers()
                
                payload = {
                    "model": self.default_model,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 1
                }
                
                async with session.post(url, json=payload, headers=headers, timeout=10) as response:
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
        """List available DeepSeek models"""
        # Known DeepSeek models
        models = [
            ModelInfo(
                id="deepseek-chat",
                name="DeepSeek Chat",
                provider=self.name,
                context_length=32768,
                description="DeepSeek's flagship chat model",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="deepseek-coder",
                name="DeepSeek Coder",
                provider=self.name,
                context_length=32768,
                description="DeepSeek's code-focused model",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="deepseek-ai",
                name="DeepSeek AI",
                provider=self.name,
                context_length=32768,
                description="DeepSeek's general-purpose AI model",
                capabilities=["chat"]
            ),
        ]
        return models
    
    async def chat(self,
                  messages: List[ChatMessage],
                  model: Optional[str] = None,
                  temperature: float = 0.7,
                  max_tokens: Optional[int] = None,
                  stream: bool = False,
                  **kwargs) -> Union[ChatResponse, AsyncGenerator[ChatResponse, None]]:
        """Send chat messages to DeepSeek"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or self.default_model
        
        # Convert messages to OpenAI-compatible format (DeepSeek uses this)
        deepseek_messages = []
        for msg in messages:
            deepseek_msg = {"role": msg.role, "content": msg.content}
            if msg.name:
                deepseek_msg["name"] = msg.name
            if msg.tool_call_id:
                deepseek_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                deepseek_msg["tool_calls"] = msg.tool_calls
            deepseek_messages.append(deepseek_msg)
        
        payload = {
            "model": model,
            "messages": deepseek_messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
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


# Singleton instance
deepseek_provider = DeepSeekProvider()