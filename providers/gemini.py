"""
Gemini Provider Implementation

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


class GeminiProvider(BaseProvider):
    """Google Gemini API provider"""
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="gemini",
            display_name="Google Gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            supports={
                ProviderCapability.CHAT: True,
                ProviderCapability.EMBEDDINGS: True,
                ProviderCapability.VISION: True,
                ProviderCapability.TOOLS: True,
                ProviderCapability.STREAMING: True,
                ProviderCapability.FUNCTION_CALLING: True,
            },
            default_model="gemini-1.5-pro",
            authentication_type="api_key",
            api_key_env_var="GEMINI_API_KEY",
            api_key_header="Authorization",
            api_key_prefix="Bearer"
        )
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Gemini API key"""
        if not credentials or "api_key" not in credentials:
            return False
        
        self.set_credentials(credentials)
        return await self.validate_credentials()
    
    async def validate_credentials(self) -> bool:
        """Validate Gemini credentials by listing models"""
        if not self._credentials or "api_key" not in self._credentials:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use a simple model list endpoint to validate
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
        """List available Gemini models"""
        # Known Gemini models (API doesn't provide a list endpoint)
        models = [
            ModelInfo(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                provider=self.name,
                context_length=1048576,
                description="Most advanced model with long context",
                capabilities=["chat", "vision", "tools"]
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                provider=self.name,
                context_length=1048576,
                description="Fast and efficient model with long context",
                capabilities=["chat", "vision"]
            ),
            ModelInfo(
                id="gemini-1.0-pro",
                name="Gemini 1.0 Pro",
                provider=self.name,
                context_length=32768,
                description="Previous generation pro model",
                capabilities=["chat", "vision"]
            ),
            ModelInfo(
                id="gemini-1.0-ultra",
                name="Gemini 1.0 Ultra",
                provider=self.name,
                context_length=32768,
                description="Most capable model for complex tasks",
                capabilities=["chat", "vision"]
            ),
            ModelInfo(
                id="gemini-2.0-flash",
                name="Gemini 2.0 Flash",
                provider=self.name,
                context_length=1048576,
                description="Next generation fast model",
                capabilities=["chat", "vision", "tools"]
            ),
            ModelInfo(
                id="embedding-001",
                name="Embedding Model",
                provider=self.name,
                context_length=2048,
                description="Text embedding model",
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
        """Send chat messages to Gemini"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or self.default_model
        
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            gemini_msg = {"role": msg.role, "parts": [{"text": msg.content}]}
            if msg.role == "user" and msg.content:
                gemini_msg["parts"] = [{"text": msg.content}]
            elif msg.role == "assistant":
                gemini_msg["parts"] = [{"text": msg.content}]
            elif msg.role == "system":
                gemini_msg["parts"] = [{"text": msg.content}]
            gemini_messages.append(gemini_msg)
        
        # Build the request payload
        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        
        # Add tools if provided
        if kwargs.get("tools"):
            payload["tools"] = kwargs["tools"]
        if kwargs.get("toolConfig"):
            payload["toolConfig"] = kwargs["toolConfig"]
        
        if stream:
            return self._chat_stream(model, payload)
        else:
            return await self._chat_single(model, payload)
    
    async def _chat_single(self, model: str, payload: Dict[str, Any]) -> ChatResponse:
        """Single chat completion (non-streaming)"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/models/{model}:generateContent"
                headers = self.get_headers()
                
                async with session.post(url, json=payload, headers=headers, timeout=120) as response:
                    if response.status == 200:
                        data = await response.json()
                        candidate = data.get("candidates", [{}])[0]
                        content = candidate.get("content", {})
                        
                        return ChatResponse(
                            content=content.get("parts", [{}])[0].get("text", ""),
                            model=model,
                            provider=self.name,
                            finish_reason=candidate.get("finishReason", "unknown"),
                            usage=data.get("usageMetadata", {}),
                            tool_calls=content.get("parts", [])
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
    
    async def _chat_stream(self, model: str, payload: Dict[str, Any]) -> AsyncGenerator[ChatResponse, None]:
        """Streaming chat completion"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/models/{model}:streamGenerateContent"
                headers = self.get_headers()
                
                async with session.post(url, json=payload, headers=headers, timeout=120) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str:
                                    try:
                                        data = json.loads(line_str)
                                        candidate = data.get("candidates", [{}])[0]
                                        if candidate and "content" in candidate:
                                            content = candidate["content"]
                                            text = content.get("parts", [{}])[0].get("text", "")
                                            if text:
                                                yield ChatResponse(
                                                    content=text,
                                                    model=model,
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
        """Generate embeddings with Gemini"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or "embedding-001"
        
        if isinstance(input, str):
            input = [input]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/models/{model}:embedContent"
                headers = self.get_headers()
                
                payload = {
                    "contents": [{"text": text} for text in input]
                }
                
                async with session.post(url, json=payload, headers=headers, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        embeddings = [
                            embeddings.get("values", [])
                            for embeddings in data.get("embedding", {}).get("values", [])
                        ]
                        return EmbeddingResponse(
                            embeddings=embeddings,
                            model=model,
                            provider=self.name,
                            usage=data.get("usageMetadata", {})
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
gemini_provider = GeminiProvider()