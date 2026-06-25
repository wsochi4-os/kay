"""
Credential Store

Manages credential storage and retrieval for all providers.
"""

import os
import json
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from .storage import SecureStorage


@dataclass
class CredentialStore:
    """
    Credential Store
    
    Manages storage and retrieval of credentials for all providers.
    """
    storage: SecureStorage
    credentials: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Load credentials from storage"""
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load all credentials from secure storage"""
        try:
            # Load from storage
            stored = self.storage.get("credentials")
            if stored:
                self.credentials = json.loads(stored)
            else:
                self.credentials = {}
        except Exception:
            self.credentials = {}
    
    def _save_credentials(self) -> None:
        """Save all credentials to secure storage"""
        try:
            self.storage.set("credentials", json.dumps(self.credentials))
        except Exception:
            pass  # Silently fail to avoid breaking the application
    
    def set_credentials(self, provider_name: str, credentials: Dict[str, str]) -> None:
        """
        Set credentials for a provider.
        
        Args:
            provider_name: Name of the provider
            credentials: Dictionary of credentials (e.g., {"api_key": "sk-..."})
        """
        self.credentials[provider_name] = credentials
        self._save_credentials()
    
    def get_credentials(self, provider_name: str) -> Optional[Dict[str, str]]:
        """
        Get credentials for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Dictionary of credentials, or None if not found
        """
        return self.credentials.get(provider_name)
    
    def get_api_key(self, provider_name: str) -> Optional[str]:
        """
        Get the API key for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            API key string, or None if not found
        """
        credentials = self.get_credentials(provider_name)
        if credentials:
            return credentials.get("api_key")
        return None
    
    def clear_credentials(self, provider_name: str) -> None:
        """
        Clear credentials for a provider.
        
        Args:
            provider_name: Name of the provider
        """
        if provider_name in self.credentials:
            del self.credentials[provider_name]
            self._save_credentials()
    
    def clear_all_credentials(self) -> None:
        """Clear all stored credentials"""
        self.credentials.clear()
        self._save_credentials()
    
    def has_credentials(self, provider_name: str) -> bool:
        """
        Check if credentials exist for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if credentials exist, False otherwise
        """
        return provider_name in self.credentials
    
    def list_providers_with_credentials(self) -> list:
        """
        List all providers that have stored credentials.
        
        Returns:
            List of provider names with stored credentials
        """
        return list(self.credentials.keys())
    
    def export_credentials(self) -> Dict[str, Dict[str, str]]:
        """
        Export all credentials (for backup purposes).
        
        Returns:
            Dictionary of all credentials
        """
        return dict(self.credentials)
    
    def import_credentials(self, credentials: Dict[str, Dict[str, str]]) -> None:
        """
        Import credentials from a dictionary.
        
        Args:
            credentials: Dictionary of credentials to import
        """
        self.credentials.update(credentials)
        self._save_credentials()
    
    def __len__(self) -> int:
        """Number of stored credential sets"""
        return len(self.credentials)
    
    def __repr__(self) -> str:
        return f"<CredentialStore with {len(self)} credential sets>"
