"""
Together Provider Implementation

Supports:
- Chat completions
- Embeddings
- Model listing
- Tool calling
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


class TogetherProvider(BaseProvider):
    """Together AI API provider"""
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="together",
            display_name="Together AI",
            base_url="https://api.together.xyz/v1",
            supports={
                ProviderCapability.CHAT: True,
                ProviderCapability.EMBEDDINGS: True,
                ProviderCapability.VISION: True,
                ProviderCapability.TOOLS: False,
                ProviderCapability.STREAMING: True,
                ProviderCapability.FUNCTION_CALLING: False,
            },
            default_model="meta-llama/Llama-3.1-405B-Instruct-Turbo",
            authentication_type="api_key",
            api_key_env_var="TOGETHER_API_KEY",
            api_key_header="Authorization",
            api_key_prefix="Bearer"
        )
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Together API key"""
        if not credentials or "api_key" not in credentials:
            return False
        
        self.set_credentials(credentials)
        return await self.validate_credentials()
    
    async def validate_credentials(self) -> bool:
        """Validate Together credentials by listing models"""
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
        """List available Together models"""
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
                            models.append(ModelInfo(
                                id=model_id,
                                name=model_data.get("name", model_id),
                                provider=self.name,
                                context_length=model_data.get("context_length", 0),
                                description=model_data.get("description", ""),
                                capabilities=["chat"]
                            ))
                        return models
                    else:
                        # Fallback to known models if API fails
                        return self._get_known_models()
        except Exception:
            return self._get_known_models()
    
    def _get_known_models(self) -> List[ModelInfo]:
        """Get known Together models as fallback"""
        models = [
            ModelInfo(
                id="meta-llama/Llama-3.1-405B-Instruct-Turbo",
                name="Llama 3.1 405B Instruct Turbo",
                provider=self.name,
                context_length=131072,
                description="Meta Llama 3.1 405B instruction-tuned model (Turbo)",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="meta-llama/Llama-3.1-70B-Instruct-Turbo",
                name="Llama 3.1 70B Instruct Turbo",
                provider=self.name,
                context_length=131072,
                description="Meta Llama 3.1 70B instruction-tuned model (Turbo)",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="meta-llama/Llama-3.1-8B-Instruct-Turbo",
                name="Llama 3.1 8B Instruct Turbo",
                provider=self.name,
                context_length=131072,
                description="Meta Llama 3.1 8B instruction-tuned model (Turbo)",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="meta-llama/Llama-3-70B-Instruct-Turbo",
                name="Llama 3 70B Instruct Turbo",
                provider=self.name,
                context_length=8192,
                description="Meta Llama 3 70B instruction-tuned model (Turbo)",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="meta-llama/Llama-3-8B-Instruct-Turbo",
                name="Llama 3 8B Instruct Turbo",
                provider=self.name,
                context_length=8192,
                description="Meta Llama 3 8B instruction-tuned model (Turbo)",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="mistralai/Mixtral-8x7B-Instruct-v0.1",
                name="Mixtral 8x7B Instruct",
                provider=self.name,
                context_length=32768,
                description="Mixtral 8x7B instruction-tuned model",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="mistralai/Mixtral-8x22B-Instruct-v0.1",
                name="Mixtral 8x22B Instruct",
                provider=self.name,
                context_length=65536,
                description="Mixtral 8x22B instruction-tuned model",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="Qwen/Qwen2-72B-Instruct",
                name="Qwen2 72B Instruct",
                provider=self.name,
                context_length=32768,
                description="Alibaba Qwen2 72B instruction-tuned model",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="google/gemma-2-27b-it",
                name="Gemma 2 27B Instruct",
                provider=self.name,
                context_length=8192,
                description="Google Gemma 2 27B instruction-tuned model",
                capabilities=["chat"]
            ),
            ModelInfo(
                id="togethercomputer/Embedding-1",
                name="Together Embedding Model",
                provider=self.name,
                context_length=8192,
                description="Together's embedding model",
                capabilities=["embeddings"]
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
        """Send chat messages to Together"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or self.default_model
        
        # Convert messages to Together format (OpenAI-compatible)
        together_messages = []
        for msg in messages:
            together_msg = {"role": msg.role, "content": msg.content}
            if msg.name:
                together_msg["name"] = msg.name
            if msg.tool_call_id:
                together_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                together_msg["tool_calls"] = msg.tool_calls
            together_messages.append(together_msg)
        
        payload = {
            "model": model,
            "messages": together_messages,
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
    
    async def embeddings(self,
                        input: Union[str, List[str]],
                        model: Optional[str] = None,
                        **kwargs) -> EmbeddingResponse:
        """Generate embeddings with Together"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or "togethercomputer/Embedding-1"
        
        if isinstance(input, str):
            input = [input]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/embeddings"
                headers = self.get_headers()
                
                payload = {
                    "model": model,
                    "input": input
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
together_provider = TogetherProvider()