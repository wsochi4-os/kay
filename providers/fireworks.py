"""
Fireworks Provider Implementation

Supports:
- Chat completions
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


class FireworksProvider(BaseProvider):
    """Fireworks AI API provider"""
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="fireworks",
            display_name="Fireworks AI",
            base_url="https://api.fireworks.ai/inference/v1",
            supports={
                ProviderCapability.CHAT: True,
                ProviderCapability.EMBEDDINGS: False,
                ProviderCapability.VISION: True,
                ProviderCapability.TOOLS: True,
                ProviderCapability.STREAMING: True,
                ProviderCapability.FUNCTION_CALLING: True,
            },
            default_model="accounts/fireworks/models/llama-v3p1-405b-instruct",
            authentication_type="api_key",
            api_key_env_var="FIREWORKS_API_KEY",
            api_key_header="Authorization",
            api_key_prefix="Bearer"
        )
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Fireworks API key"""
        if not credentials or "api_key" not in credentials:
            return False
        
        self.set_credentials(credentials)
        return await self.validate_credentials()
    
    async def validate_credentials(self) -> bool:
        """Validate Fireworks credentials by making a test request"""
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
        """List available Fireworks models"""
        # Known Fireworks models
        models = [
            ModelInfo(
                id="accounts/fireworks/models/llama-v3p1-405b-instruct",
                name="Llama 3.1 405B Instruct",
                provider=self.name,
                context_length=131072,
                description="Meta Llama 3.1 405B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/llama-v3p1-70b-instruct",
                name="Llama 3.1 70B Instruct",
                provider=self.name,
                context_length=131072,
                description="Meta Llama 3.1 70B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/llama-v3p1-8b-instruct",
                name="Llama 3.1 8B Instruct",
                provider=self.name,
                context_length=131072,
                description="Meta Llama 3.1 8B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/llama-v3-70b-instruct",
                name="Llama 3 70B Instruct",
                provider=self.name,
                context_length=8192,
                description="Meta Llama 3 70B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/llama-v3-8b-instruct",
                name="Llama 3 8B Instruct",
                provider=self.name,
                context_length=8192,
                description="Meta Llama 3 8B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/mixtral-8x7b-instruct",
                name="Mixtral 8x7B Instruct",
                provider=self.name,
                context_length=32768,
                description="Mixtral 8x7B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/mixtral-8x22b-instruct",
                name="Mixtral 8x22B Instruct",
                provider=self.name,
                context_length=65536,
                description="Mixtral 8x22B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/qwen2-72b-instruct",
                name="Qwen2 72B Instruct",
                provider=self.name,
                context_length=32768,
                description="Alibaba Qwen2 72B instruction-tuned model",
                capabilities=["chat", "tools"]
            ),
            ModelInfo(
                id="accounts/fireworks/models/gemma-2-27b-it",
                name="Gemma 2 27B Instruct",
                provider=self.name,
                context_length=8192,
                description="Google Gemma 2 27B instruction-tuned model",
                capabilities=["chat", "tools"]
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
        """Send chat messages to Fireworks"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or self.default_model
        
        # Convert messages to OpenAI-compatible format (Fireworks uses this)
        fireworks_messages = []
        for msg in messages:
            fireworks_msg = {"role": msg.role, "content": msg.content}
            if msg.name:
                fireworks_msg["name"] = msg.name
            if msg.tool_call_id:
                fireworks_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                fireworks_msg["tool_calls"] = msg.tool_calls
            fireworks_messages.append(fireworks_msg)
        
        payload = {
            "model": model,
            "messages": fireworks_messages,
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


# Singleton instance
fireworks_provider = FireworksProvider()