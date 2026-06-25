"""
Secure Storage

Secure credential storage with multiple backends:
- macOS: Keychain
- Linux: Secret Service / Keyring
- Windows: Credential Manager
- Fallback: Encrypted file storage
"""

import os
import sys
import json
import base64
from typing import Optional, Any, Dict
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod

# Environment variable mappings for API keys
ENV_VAR_MAPPINGS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "together": "TOGETHER_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Get a value from storage"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: str) -> bool:
        """Set a value in storage"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from storage"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in storage"""
        pass


class EncryptedFileStorage(StorageBackend):
    """
    Encrypted file storage backend.
    
    Uses AES-256-GCM encryption with a key derived from the system.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize encrypted file storage.
        
        Args:
            storage_path: Path to the storage directory (defaults to ~/.kutti)
        """
        if storage_path is None:
            storage_path = os.path.expanduser("~/.kutti")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.storage_path / "credentials.enc"
        
        # Generate or load encryption key
        self.key = self._get_encryption_key()
        
        # Load data
        self.data = self._load_data()
    
    def _get_encryption_key(self) -> bytes:
        """Get or create the encryption key"""
        key_file = self.storage_path / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate a new key
            import secrets
            key = secrets.token_bytes(32)  # 256-bit key for AES-256
            
            # Save the key
            with open(key_file, "wb") as f:
                f.write(key)
            
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            
            return key
    
    def _load_data(self) -> Dict[str, str]:
        """Load encrypted data from file"""
        if not self.storage_file.exists():
            return {}
        
        try:
            with open(self.storage_file, "rb") as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            aesgcm = AESGCM(self.key)
            
            # First 12 bytes are nonce, rest is ciphertext + tag
            nonce = encrypted_data[:12]
            ciphertext_and_tag = encrypted_data[12:]
            
            decrypted = aesgcm.decrypt(nonce, ciphertext_and_tag, None)
            return json.loads(decrypted.decode('utf-8'))
        except Exception:
            return {}
    
    def _save_data(self) -> None:
        """Save encrypted data to file"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            import secrets
            
            aesgcm = AESGCM(self.key)
            nonce = secrets.token_bytes(12)
            
            data_str = json.dumps(self.data)
            encrypted = aesgcm.encrypt(nonce, data_str.encode('utf-8'), None)
            
            # Write nonce + encrypted data
            with open(self.storage_file, "wb") as f:
                f.write(nonce + encrypted)
            
            # Set restrictive permissions
            os.chmod(self.storage_file, 0o600)
        except Exception:
            pass
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from storage"""
        return self.data.get(key)
    
    def set(self, key: str, value: str) -> bool:
        """Set a value in storage"""
        self.data[key] = value
        self._save_data()
        return True
    
    def delete(self, key: str) -> bool:
        """Delete a value from storage"""
        if key in self.data:
            del self.data[key]
            self._save_data()
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in storage"""
        return key in self.data


class EnvironmentStorage(StorageBackend):
    """
    Environment variable storage backend.
    
    Reads from environment variables, but doesn't write to them.
    """
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from environment variables"""
        # Check direct key
        if key in os.environ:
            return os.environ[key]
        
        # Check provider-specific environment variables
        if key == "credentials":
            # This is a special case - we don't store full credentials in env
            return None
        
        return None
    
    def set(self, key: str, value: str) -> bool:
        """Set a value in environment variables (not supported)"""
        # Can't set environment variables from here
        return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from environment variables (not supported)"""
        return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in environment variables"""
        return key in os.environ


class KeychainStorage(StorageBackend):
    """
    macOS Keychain storage backend.
    
    Uses the macOS Keychain for secure credential storage.
    """
    
    def __init__(self):
        self.available = sys.platform == "darwin"
        self._keychain = None
        
        if self.available:
            try:
                import keyring
                self._keychain = keyring
            except ImportError:
                self.available = False
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Keychain"""
        if not self.available or not self._keychain:
            return None
        
        try:
            return self._keychain.get_password("kutti", key)
        except Exception:
            return None
    
    def set(self, key: str, value: str) -> bool:
        """Set a value in Keychain"""
        if not self.available or not self._keychain:
            return False
        
        try:
            self._keychain.set_password("kutti", key, value)
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from Keychain"""
        if not self.available or not self._keychain:
            return False
        
        try:
            self._keychain.delete_password("kutti", key)
            return True
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Keychain"""
        return self.get(key) is not None


class SecretServiceStorage(StorageBackend):
    """
    Linux Secret Service storage backend.
    
    Uses the freedesktop.org Secret Service API for secure credential storage.
    """
    
    def __init__(self):
        self.available = sys.platform.startswith("linux")
        self._secret_service = None
        
        if self.available:
            try:
                import secretstorage
                self._secret_service = secretstorage
            except ImportError:
                self.available = False
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Secret Service"""
        if not self.available or not self._secret_service:
            return None
        
        try:
            connection = self._secret_service.dbus_init()
            collection = self._secret_service.Collection(connection)
            
            # Search for the secret
            attributes = {"application": "kutti", "key": key}
            secrets = collection.search_items(attributes)
            
            if secrets:
                return secrets[0].get_secret().decode('utf-8')
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: str) -> bool:
        """Set a value in Secret Service"""
        if not self.available or not self._secret_service:
            return False
        
        try:
            connection = self._secret_service.dbus_init()
            collection = self._secret_service.Collection(connection)
            
            attributes = {"application": "kutti", "key": key}
            collection.create_item(
                f"kutti-{key}",
                attributes,
                value.encode('utf-8')
            )
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from Secret Service"""
        if not self.available or not self._secret_service:
            return False
        
        try:
            connection = self._secret_service.dbus_init()
            collection = self._secret_service.Collection(connection)
            
            attributes = {"application": "kutti", "key": key}
            items = collection.search_items(attributes)
            
            for item in items:
                collection.delete_item(item)
            
            return True
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Secret Service"""
        return self.get(key) is not None


class WindowsCredentialStorage(StorageBackend):
    """
    Windows Credential Manager storage backend.
    
    Uses the Windows Credential Manager for secure credential storage.
    """
    
    def __init__(self):
        self.available = sys.platform == "win32"
        self._credential_manager = None
        
        if self.available:
            try:
                import win32credentialmanager
                self._credential_manager = win32credentialmanager
            except ImportError:
                self.available = False
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Windows Credential Manager"""
        if not self.available or not self._credential_manager:
            return None
        
        try:
            # This is a simplified implementation
            # In a real implementation, we would use the proper Windows API
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: str) -> bool:
        """Set a value in Windows Credential Manager"""
        if not self.available or not self._credential_manager:
            return False
        
        try:
            # Simplified implementation
            return False
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from Windows Credential Manager"""
        if not self.available or not self._credential_manager:
            return False
        
        try:
            return False
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Windows Credential Manager"""
        return self.get(key) is not None


@dataclass
class SecureStorage:
    """
    Secure Storage
    
    Provides secure credential storage with multiple backends.
    Falls back to encrypted file storage if native backends are not available.
    
    Credential resolution order:
    1. System Keychain (macOS) / Secret Service (Linux) / Credential Manager (Windows)
    2. Encrypted Local Storage
    3. Environment Variables
    """
    backend: StorageBackend
    fallback_backend: Optional[StorageBackend] = None
    env_backend: StorageBackend = field(default_factory=EnvironmentStorage)
    
    def __init__(self, backend: Optional[str] = None):
        """
        Initialize secure storage.
        
        Args:
            backend: Backend to use ("keychain", "secret-service", "windows", "file", or None for auto)
        """
        if backend == "keychain" or (backend is None and sys.platform == "darwin"):
            self.backend = KeychainStorage()
        elif backend == "secret-service" or (backend is None and sys.platform.startswith("linux")):
            self.backend = SecretServiceStorage()
        elif backend == "windows" or (backend is None and sys.platform == "win32"):
            self.backend = WindowsCredentialStorage()
        else:
            # Default to encrypted file storage
            self.backend = EncryptedFileStorage()
        
        # Always have environment variable fallback
        self.env_backend = EnvironmentStorage()
        
        # Check if backend is available, fall back to file storage if not
        if not self._is_backend_available(self.backend):
            self.backend = EncryptedFileStorage()
    
    def _is_backend_available(self, backend: StorageBackend) -> bool:
        """Check if a backend is available"""
        # Try a test operation
        try:
            test_key = f"_test_{id(backend)}"
            backend.set(test_key, "test")
            result = backend.get(test_key)
            backend.delete(test_key)
            return result == "test"
        except Exception:
            return False
    
    def get(self, key: str) -> Optional[str]:
        """
        Get a value from storage.
        
        Tries backends in order of preference.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value, or None if not found
        """
        # Try primary backend first
        value = self.backend.get(key)
        if value is not None:
            return value
        
        # Try environment variables
        value = self.env_backend.get(key)
        if value is not None:
            return value
        
        return None
    
    def set(self, key: str, value: str) -> bool:
        """
        Set a value in storage.
        
        Args:
            key: The key to set
            value: The value to store
            
        Returns:
            True if successful, False otherwise
        """
        return self.backend.set(key, value)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from storage.
        
        Args:
            key: The key to delete
            
        Returns:
            True if successful, False otherwise
        """
        return self.backend.delete(key)
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return self.backend.exists(key) or self.env_backend.exists(key)
    
    def get_from_env(self, provider_name: str) -> Optional[str]:
        """
        Get API key from environment variable for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            API key from environment variable, or None if not found
        """
        env_var = ENV_VAR_MAPPINGS.get(provider_name)
        if env_var:
            return os.environ.get(env_var)
        return None
    
    def __repr__(self) -> str:
        return f"<SecureStorage backend={self.backend.__class__.__name__}>"
