"""
Authentication Manager

Responsibilities:
- Login
- Logout
- Switch provider
- Refresh tokens
- Validate credentials
- Track active sessions
"""

import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import asyncio

from providers.base import BaseProvider, ProviderError, AuthenticationError
from providers.registry import registry
from .credentials import CredentialStore
from .storage import SecureStorage
from .session import SessionManager


@dataclass
class AuthManager:
    """
    Authentication Manager
    
    Handles all authentication operations for providers.
    """
    credential_store: CredentialStore
    storage: SecureStorage
    session_manager: SessionManager
    
    def __init__(self, storage_backend: Optional[str] = None):
        """
        Initialize the authentication manager.
        
        Args:
            storage_backend: Storage backend to use (None for auto-detect)
        """
        self.storage = SecureStorage(backend=storage_backend)
        self.credential_store = CredentialStore(self.storage)
        self.session_manager = SessionManager(self.credential_store)
    
    async def login(self, 
                   provider_name: str, 
                   api_key: Optional[str] = None,
                   credentials: Optional[Dict[str, str]] = None) -> bool:
        """
        Login to a provider.
        
        Args:
            provider_name: Name of the provider to authenticate with
            api_key: API key (optional, will prompt if not provided)
            credentials: Full credentials dictionary (alternative to api_key)
            
        Returns:
            True if login succeeded, False otherwise
            
        Raises:
            ProviderError: If provider doesn't exist
        """
        # Get the provider
        provider = registry.get(provider_name)
        if not provider:
            raise ProviderError(f"Provider '{provider_name}' not found", "auth")
        
        # Use provided credentials or api_key
        if credentials:
            creds = credentials
        elif api_key:
            creds = {"api_key": api_key}
        else:
            # Try to get from environment variable
            env_var = provider.info.api_key_env_var
            if env_var and env_var in os.environ:
                creds = {"api_key": os.environ[env_var]}
            else:
                # Would normally prompt here, but we'll return False
                return False
        
        # Authenticate with the provider
        success = await provider.authenticate(creds)
        
        if success:
            # Validate credentials
            valid = await provider.validate_credentials()
            if valid:
                # Store credentials
                self.credential_store.set_credentials(provider_name, creds)
                
                # Create session
                self.session_manager.create_session(provider_name)
                
                return True
            else:
                # Don't store invalid credentials
                provider.clear_credentials()
                return False
        else:
            return False
    
    async def logout(self, provider_name: str) -> bool:
        """
        Logout from a provider.
        
        Args:
            provider_name: Name of the provider to logout from
            
        Returns:
            True if logout succeeded, False otherwise
        """
        # Clear credentials
        self.credential_store.clear_credentials(provider_name)
        
        # Clear session
        self.session_manager.clear_session(provider_name)
        
        # Clear provider credentials
        provider = registry.get(provider_name)
        if provider:
            provider.clear_credentials()
        
        return True
    
    async def logout_all(self) -> int:
        """
        Logout from all providers.
        
        Returns:
            Number of providers logged out from
        """
        count = 0
        for provider_name in registry.list():
            if self.logout(provider_name):
                count += 1
        return count
    
    async def switch_provider(self, provider_name: str) -> bool:
        """
        Switch to a different provider.
        
        Args:
            provider_name: Name of the provider to switch to
            
        Returns:
            True if switch succeeded, False otherwise
            
        Raises:
            ProviderError: If provider doesn't exist or not authenticated
        """
        # Check if provider exists
        if provider_name not in registry:
            raise ProviderError(f"Provider '{provider_name}' not found", "auth")
        
        # Check if authenticated
        if not self.is_authenticated(provider_name):
            raise ProviderError(f"Not authenticated with '{provider_name}'", "auth")
        
        # Set as active provider
        self.session_manager.set_active_provider(provider_name)
        
        return True
    
    async def refresh_token(self, provider_name: str) -> bool:
        """
        Refresh authentication token for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if token refresh succeeded, False otherwise
        """
        provider = registry.get(provider_name)
        if not provider:
            return False
        
        # Get current credentials
        credentials = self.credential_store.get_credentials(provider_name)
        if not credentials:
            return False
        
        # Set credentials on provider
        provider.set_credentials(credentials)
        
        # Attempt to refresh token
        success = await provider.refresh_token()
        
        if success:
            # Update stored credentials if they changed
            new_credentials = provider.get_credentials()
            if new_credentials and new_credentials != credentials:
                self.credential_store.set_credentials(provider_name, new_credentials)
        
        return success
    
    async def validate_credentials(self, provider_name: str) -> bool:
        """
        Validate credentials for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if credentials are valid, False otherwise
        """
        provider = registry.get(provider_name)
        if not provider:
            return False
        
        # Get credentials
        credentials = self.credential_store.get_credentials(provider_name)
        if not credentials:
            return False
        
        # Set credentials on provider
        provider.set_credentials(credentials)
        
        # Validate
        return await provider.validate_credentials()
    
    def is_authenticated(self, provider_name: Optional[str] = None) -> bool:
        """
        Check if authenticated with a provider.
        
        Args:
            provider_name: Name of the provider (None for active provider)
            
        Returns:
            True if authenticated, False otherwise
        """
        if provider_name is None:
            provider_name = self.get_active_provider()
        
        if not provider_name:
            return False
        
        # Check if we have credentials
        credentials = self.credential_store.get_credentials(provider_name)
        if not credentials:
            return False
        
        # Check if provider exists
        provider = registry.get(provider_name)
        if not provider:
            return False
        
        return True
    
    def get_active_provider(self) -> Optional[str]:
        """
        Get the currently active provider.
        
        Returns:
            Name of the active provider, or None if none set
        """
        return self.session_manager.get_active_provider()
    
    def set_active_provider(self, provider_name: str) -> None:
        """
        Set the active provider.
        
        Args:
            provider_name: Name of the provider to set as active
        """
        self.session_manager.set_active_provider(provider_name)
    
    def get_authenticated_providers(self) -> List[str]:
        """
        Get list of all authenticated providers.
        
        Returns:
            List of provider names that are authenticated
        """
        authenticated = []
        for provider_name in registry.list():
            if self.is_authenticated(provider_name):
                authenticated.append(provider_name)
        return authenticated
    
    def get_active_session(self) -> Optional[Dict[str, Any]]:
        """
        Get the active session information.
        
        Returns:
            Session information dictionary, or None if no active session
        """
        return self.session_manager.get_active_session()
    
    def get_session(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get session information for a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Session information dictionary, or None if no session
        """
        return self.session_manager.get_session(provider_name)
    
    async def get_provider(self, provider_name: Optional[str] = None) -> Optional[BaseProvider]:
        """
        Get a provider instance with credentials loaded.
        
        Args:
            provider_name: Name of the provider (None for active provider)
            
        Returns:
            Provider instance with credentials set, or None if not found/authenticated
        """
        if provider_name is None:
            provider_name = self.get_active_provider()
        
        if not provider_name:
            return None
        
        provider = registry.get(provider_name)
        if not provider:
            return None
        
        # Load credentials
        credentials = self.credential_store.get_credentials(provider_name)
        if credentials:
            provider.set_credentials(credentials)
        
        return provider
    
    def list_providers(self) -> List[str]:
        """
        List all available providers.
        
        Returns:
            List of all provider names
        """
        return registry.list()
    
    def list_authenticated_providers(self) -> List[str]:
        """
        List all authenticated providers.
        
        Returns:
            List of authenticated provider names
        """
        return self.get_authenticated_providers()
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider information dictionary, or None if not found
        """
        provider = registry.get(provider_name)
        if not provider:
            return None
        
        info = provider.info
        return {
            "name": info.name,
            "display_name": info.display_name,
            "base_url": info.base_url,
            "supports": {k.value: v for k, v in info.supports.items()},
            "default_model": info.default_model,
            "authentication_type": info.authentication_type,
            "api_key_env_var": info.api_key_env_var,
            "authenticated": self.is_authenticated(provider_name)
        }
    
    def __repr__(self) -> str:
        active = self.get_active_provider() or "None"
        authenticated = len(self.get_authenticated_providers())
        return f"<AuthManager active={active} authenticated={authenticated}/{len(registry)}>"


# Global auth manager instance
auth_manager = AuthManager()


# Convenience functions for direct use
def login(provider_name: str, api_key: Optional[str] = None) -> bool:
    """Login to a provider (synchronous wrapper)"""
    import asyncio
    return asyncio.run(auth_manager.login(provider_name, api_key))


def logout(provider_name: str) -> bool:
    """Logout from a provider (synchronous wrapper)"""
    import asyncio
    return asyncio.run(auth_manager.logout(provider_name))


def active_provider() -> Optional[str]:
    """Get the active provider"""
    return auth_manager.get_active_provider()


def is_authenticated(provider_name: Optional[str] = None) -> bool:
    """Check if authenticated"""
    return auth_manager.is_authenticated(provider_name)
