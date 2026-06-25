"""
CLI Login Command

kutti login PROVIDER
"""

import argparse
import sys
import os
from typing import Optional, List

from providers.registry import registry
from auth.manager import auth_manager


def create_login_parser(parser: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    """
    Create the login command parser.
    
    Args:
        parser: Parent parser (optional)
        
    Returns:
        Argument parser for login command
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Login to an AI provider")
    else:
        parser = parser.add_parser(
            "login",
            help="Login to an AI provider",
            description="Login to an AI provider and store credentials securely"
        )
    
    parser.add_argument(
        "provider",
        nargs="?",
        help="Name of the provider to login to (e.g., openai, groq, anthropic)"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="API key for the provider (optional, will prompt if not provided)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available providers"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force re-authentication even if already logged in"
    )
    
    return parser


def login_command(args: argparse.Namespace) -> int:
    """
    Execute the login command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    import asyncio
    
    # List providers
    if args.list:
        print("Available providers:")
        for provider_name in registry.list():
            provider = registry.get(provider_name)
            if provider:
                info = provider.info
                authenticated = auth_manager.is_authenticated(provider_name)
                active = auth_manager.get_active_provider() == provider_name
                
                auth_status = "✓" if authenticated else "✗"
                active_status = " [active]" if active else ""
                
                print(f"  {auth_status} {provider_name:15} {info.display_name}{active_status}")
        
        return 0
    
    # Check if provider is specified
    if not args.provider:
        print("Error: Provider name is required")
        print("Usage: kutti login <provider> [--api-key KEY]")
        print("\nAvailable providers:")
        for provider_name in registry.list():
            provider = registry.get(provider_name)
            if provider:
                print(f"  - {provider_name}")
        return 1
    
    # Check if provider exists
    if args.provider not in registry:
        print(f"Error: Provider '{args.provider}' not found")
        print("\nAvailable providers:")
        for provider_name in registry.list():
            print(f"  - {provider_name}")
        return 1
    
    # Check if already authenticated (unless force)
    if not args.force and auth_manager.is_authenticated(args.provider):
        print(f"Already authenticated with {args.provider}")
        return 0
    
    # Get API key
    api_key = args.api_key
    
    if not api_key:
        # Try environment variable
        provider = registry.get(args.provider)
        if provider:
            env_var = provider.info.api_key_env_var
            if env_var and env_var in os.environ:
                api_key = os.environ[env_var]
                print(f"Using API key from {env_var} environment variable")
    
    if not api_key:
        # Prompt for API key
        try:
            api_key = input(f"Enter API key for {args.provider}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLogin cancelled")
            return 1
    
    if not api_key:
        print("Error: API key is required")
        return 1
    
    # Login
    print(f"Authenticating with {args.provider}...")
    
    try:
        import asyncio
        success = asyncio.run(auth_manager.login(args.provider, api_key=api_key))
        
        if success:
            print(f"✓ Successfully authenticated with {args.provider}")
            
            # Set as active provider if it's the first one
            if auth_manager.get_active_provider() is None:
                auth_manager.set_active_provider(args.provider)
                print(f"  Set as active provider")
            
            return 0
        else:
            print(f"✗ Authentication failed for {args.provider}")
            print("  Invalid API key or authentication error")
            return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def main():
    """Main entry point for login command"""
    parser = create_login_parser()
    args = parser.parse_args()
    sys.exit(login_command(args))


if __name__ == "__main__":
    main()
