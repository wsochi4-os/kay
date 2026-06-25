# Kutti - Your Personal AI CLI Agent
# OpenCode-compatible authentication & provider system

__version__ = "0.1.0"

# Import key modules for easy access
from providers.registry import registry
from auth.manager import auth_manager
from models.registry import model_registry
from router.chat import router
from auth.storage import SecureStorage

# Initialize the system
def initialize():
    """Initialize the Kutti system"""
    # The registry is already initialized on import
    pass

# Clean up imports
__all__ = [
    "registry",
    "auth_manager", 
    "model_registry",
    "router",
    "SecureStorage",
    "initialize",
    "__version__",
]