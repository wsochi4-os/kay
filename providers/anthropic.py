"""
Anthropic Provider Implementation

Supports:
- Chat completions (Messages API)
- Model listing
- Tool calling
- Streaming
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
    AuthenticationError,
    ProviderError
)


class AnthropicProvider(BaseProvider):
    """Anthropic API provider (Messages API)"""
    
    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="anthropic",
            display_name="Anthropic",
            base_url="https://api.anthropic.com/v1",
            supports={
                ProviderCapability.CHAT: True,
                ProviderCapability.EMBEDDINGS: False,
                ProviderCapability.VISION: True,
                ProviderCapability.TOOLS: True,
                ProviderCapability.STREAMING: True,
                ProviderCapability.FUNCTION_CALLING: True,
            },
            default_model="claude-3-5-sonnet-20250620",
            authentication_type="api_key",
            api_key_env_var="ANTHROPIC_API_KEY",
            api_key_header="x-api-key",
            api_key_prefix=""
        )
    
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Anthropic API key"""
        if not credentials or "api_key" not in credentials:
            return False
        
        self.set_credentials(credentials)
        return await self.validate_credentials()
    
    async def validate_credentials(self) -> bool:
        """Validate Anthropic credentials by listing models"""
        if not self._credentials or "api_key" not in self._credentials:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/messages"
                headers = self.get_headers()
                
                # Send a minimal request to validate
                payload = {
                    "model": self.default_model,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "test"}]
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
        """List available Anthropic models"""
        # Anthropic doesn't have a public models endpoint, so we use known models
        known_models = [
            {"id": "claude-3-5-sonnet-20250620", "name": "Claude 3.5 Sonnet", "context_length": 200000},
            {"id": "claude-3-5-sonnet-20250620-v2:1", "name": "Claude 3.5 Sonnet v2", "context_length": 200000},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context_length": 200000},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context_length": 200000},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context_length": 200000},
            {"id": "claude-2:1", "name": "Claude 2.1", "context_length": 200000},
            {"id": "claude-2", "name": "Claude 2", "context_length": 100000},
            {"id": "claude-instant-1:2", "name": "Claude Instant 1.2", "context_length": 100000},
        ]
        
        return [
            ModelInfo(
                id=model["id"],
                name=model["name"],
                provider=self.name,
                context_length=model["context_length"],
                description=f"Anthropic {model['name']} model",
                capabilities=["chat", "tools"]
            )
            for model in known_models
        ]
    
    async def chat(self,
                  messages: List[ChatMessage],
                  model: Optional[str] = None,
                  temperature: float = 0.7,
                  max_tokens: Optional[int] = None,
                  stream: bool = False,
                  **kwargs) -> Union[ChatResponse, AsyncGenerator[ChatResponse, None]]:
        """Send chat messages to Anthropic"""
        if not self._credentials or "api_key" not in self._credentials:
            raise AuthenticationError("Not authenticated", self.name)
        
        model = model or self.default_model
        max_tokens = max_tokens or 4096
        
        # Convert messages to Anthropic format
        anthropic_messages = []
        for msg in messages:
            anthropic_msg = {"role": msg.role, "content": msg.content}
            
            # Handle tool calls and results
            if msg.role == "assistant" and msg.tool_calls:
                anthropic_msg["content"] = []
                for tool_call in msg.tool_calls:
                    if isinstance(tool_call, dict):
                        anthropic_msg["content"].append({
                            "type": "tool_use",
                            "id": tool_call.get("id", ""),
                            "name": tool_call.get("function", {}).get("name", ""),
                            "input": tool_call.get("function", {}).get("arguments", "")
                        })
            elif msg.role == "tool":
                anthropic_msg["role"] = "user"
                anthropic_msg["content"] = [{
                    "type": "tool_result",
                    "tool_use_id": msg.tool_call_id or "",
                    "content": msg.content
                }]
            
            anthropic_messages.append(anthropic_msg)
        
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": anthropic_messages
        }
        
        # Add tool support if available
        if kwargs.get("tools"):
            payload["tools"] = kwargs["tools"]
        
        if stream:
            return self._chat_stream(payload)
        else:
            return await self._chat_single(payload)
    
    async def _chat_single(self, payload: Dict[str, Any]) -> ChatResponse:
        """Single chat completion (non-streaming)"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.get_base_url()}/messages"
                headers = self.get_headers()
                
                async with session.post(url, json=payload, headers=headers, timeout=120) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("content", [])
                        
                        # Extract text content
                        text_content = ""
                        tool_calls = []
                        
                        for item in content:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    text_content += item.get("text", "")
                                elif item.get("type") == "tool_use":
                                    tool_calls.append({
                                        "id": item.get("id", ""),
                                        "function": {
                                            "name": item.get("name", ""),
                                            "arguments": item.get("input", "")
                                        }
                                    })
                        
                        return ChatResponse(
                            content=text_content,
                            model=payload.get("model", self.default_model),
                            provider=self.name,
                            finish_reason=data.get("stop_reason", "unknown"),
                            usage={
                                "input_tokens": data.get("usage", {}).get("input_tokens", 0),
                                "output_tokens": data.get("usage", {}).get("output_tokens", 0)
                            },
                            tool_calls=tool_calls if tool_calls else None
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
                url = f"{self.get_base_url()}/messages"
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
                                            if "delta" in data:
                                                delta = data["delta"]
                                                if "text" in delta:
                                                    yield ChatResponse(
                                                        content=delta["text"],
                                                        model=payload.get("model", self.default_model),
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
anthropic_provider = AnthropicProvider()
