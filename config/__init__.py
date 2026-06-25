# Configuration package

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for Kutti"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (defaults to ~/.kutti/config.yaml)
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.kutti/config.yaml")
        
        self.config_path = Path(config_path)
        self.data = {}
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.data = yaml.safe_load(f) or {}
            except Exception:
                self.data = {}
        else:
            self.data = {}
    
    def _save(self) -> None:
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.data, f, default_flow_style=False)
        except Exception:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        keys = key.split('.')
        current = self.data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self._save()
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        providers = self.get("providers", {})
        return providers.get(provider_name, {})
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default settings"""
        return self.get("defaults", {})


# Global configuration instance
config = Config()

__all__ = ["Config", "config"]