"""
Session Manager

Track active sessions for all providers.
"""

import os
import json
import time
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .credentials import CredentialStore


@dataclass
class Session:
    """Session information for a provider"""
    provider: str
    model: str
    authenticated: bool = True
    login_timestamp: float = field(default_factory=time.time)
    last_used_timestamp: float = field(default_factory=time.time)
    api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary"""
        return cls(**data)
    
    def update_last_used(self) -> None:
        """Update the last used timestamp"""
        self.last_used_timestamp = time.time()
    
    def is_expired(self, ttl: float = 86400) -> bool:
        """
        Check if session is expired.
        
        Args:
            ttl: Time-to-live in seconds (default: 24 hours)
            
        Returns:
            True if session is expired, False otherwise
        """
        return (time.time() - self.login_timestamp) > ttl


@dataclass
class SessionManager:
    """
    Session Manager
    
    Tracks active sessions for all providers.
    """
    credential_store: CredentialStore
    sessions: Dict[str, Session] = field(default_factory=dict)
    active_provider: Optional[str] = None
    storage_path: Path = field(default_factory=lambda: Path.home() / ".kutti" / "sessions.json")
    
    def __post_init__(self):
        """Load sessions from storage"""
        self._load_sessions()
    
    def _load_sessions(self) -> None:
        """Load sessions from storage file"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.active_provider = data.get("active_provider")
                    
                    for provider_name, session_data in data.get("sessions", {}).items():
                        try:
                            session = Session.from_dict(session_data)
                            self.sessions[provider_name] = session
                        except Exception:
                            continue
        except Exception:
            self.sessions = {}
            self.active_provider = None
    
    def _save_sessions(self) -> None:
        """Save sessions to storage file"""
        try:
            data = {
                "active_provider": self.active_provider,
                "sessions": {name: session.to_dict() for name, session in self.sessions.items()}
            }
            
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(self.storage_path, 0o600)
        except Exception:
            pass
    
    def create_session(self, provider_name: str, model: Optional[str] = None) -> Session:
        """
        Create a new session for a provider.
        
        Args:
            provider_name: Name of the provider
            model: Model to use (defaults to provider's default)
            
        Returns:
            The created session
        """
        # Get API key from credential store
        api_key = self.credential_store.get_api_key(provider_name)
        
        # Create session
        session = Session(
            provider=provider_name,
            model=model or "",
            authenticated=api_key is not None,
            api_key=api_key
        )
        
        self.sessions[provider_name] = session
        
        # If this is the first session, set it as active
        if self.active_provider is None:
            self.active_provider = provider_name
        
        self._save_sessions()
        return session
    
    def get_session(self, provider_name: str) -> Optional[Session]:
        """
        Get session for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Session object, or None if not found
        """
        return self.sessions.get(provider_name)
    
    def get_active_session(self) -> Optional[Session]:
        """
        Get the active session.
        
        Returns:
            Active session object, or None if no active session
        """
        if self.active_provider:
            return self.get_session(self.active_provider)
        return None
    
    def set_active_provider(self, provider_name: str) -> None:
        """
        Set the active provider.
        
        Args:
            provider_name: Name of the provider to set as active
        """
        if provider_name in self.sessions or self.credential_store.has_credentials(provider_name):
            self.active_provider = provider_name
            self._save_sessions()
    
    def get_active_provider(self) -> Optional[str]:
        """
        Get the currently active provider.
        
        Returns:
            Name of the active provider, or None if none set
        """
        return self.active_provider
    
    def clear_session(self, provider_name: str) -> bool:
        """
        Clear a session.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if session was cleared, False otherwise
        """
        if provider_name in self.sessions:
            del self.sessions[provider_name]
            
            # If this was the active session, clear it
            if self.active_provider == provider_name:
                self.active_provider = None
            
            self._save_sessions()
            return True
        return False
    
    def clear_all_sessions(self) -> None:
        """Clear all sessions"""
        self.sessions.clear()
        self.active_provider = None
        self._save_sessions()
    
    def update_session_model(self, provider_name: str, model: str) -> bool:
        """
        Update the model for a session.
        
        Args:
            provider_name: Name of the provider
            model: New model to use
            
        Returns:
            True if session was updated, False otherwise
        """
        session = self.get_session(provider_name)
        if session:
            session.model = model
            session.update_last_used()
            self._save_sessions()
            return True
        return False
    
    def update_session_last_used(self, provider_name: str) -> bool:
        """
        Update the last used timestamp for a session.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if session was updated, False otherwise
        """
        session = self.get_session(provider_name)
        if session:
            session.update_last_used()
            self._save_sessions()
            return True
        return False
    
    def list_sessions(self) -> List[Session]:
        """
        List all active sessions.
        
        Returns:
            List of all session objects
        """
        return list(self.sessions.values())
    
    def list_session_providers(self) -> List[str]:
        """
        List all providers with active sessions.
        
        Returns:
            List of provider names with active sessions
        """
        return list(self.sessions.keys())
    
    def get_session_info(self, provider_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            provider_name: Name of the provider (None for active session)
            
        Returns:
            Session information dictionary, or None if not found
        """
        if provider_name is None:
            provider_name = self.active_provider
        
        if not provider_name:
            return None
        
        session = self.get_session(provider_name)
        if not session:
            return None
        
        return {
            "provider": session.provider,
            "model": session.model,
            "authenticated": session.authenticated,
            "login_timestamp": session.login_timestamp,
            "last_used_timestamp": session.last_used_timestamp
        }
    
    def cleanup_expired_sessions(self, ttl: float = 86400) -> int:
        """
        Clean up expired sessions.
        
        Args:
            ttl: Time-to-live in seconds (default: 24 hours)
            
        Returns:
            Number of sessions cleaned up
        """
        expired = []
        for provider_name, session in self.sessions.items():
            if session.is_expired(ttl):
                expired.append(provider_name)
        
        for provider_name in expired:
            self.clear_session(provider_name)
        
        return len(expired)
    
    def __len__(self) -> int:
        """Number of active sessions"""
        return len(self.sessions)
    
    def __repr__(self) -> str:
        active = self.active_provider or "None"
        return f"<SessionManager active={active} sessions={len(self)}>"
