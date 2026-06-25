"""
CLI Providers Command

kutti providers list
kutti provider use PROVIDER
"""

import argparse
import sys
from typing import Optional

from providers.registry import registry
from auth.manager import auth_manager


def create_providers_parser(parser: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    """
    Create the providers command parser.
    
    Args:
        parser: Parent parser (optional)
        
    Returns:
        Argument parser for providers command
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Manage AI providers")
    else:
        parser = parser.add_parser(
            "providers",
            help="Manage AI providers",
            description="List and manage AI providers"
        )
    
    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List all available providers",
        description="List all available AI providers and their status"
    )
    list_parser.add_argument(
        "--authenticated", "-a",
        action="store_true",
        help="Show only authenticated providers"
    )
    list_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    
    # Use command
    use_parser = subparsers.add_parser(
        "use",
        help="Set the active provider",
        description="Set the active provider for subsequent requests"
    )
    use_parser.add_argument(
        "provider",
        help="Name of the provider to use"
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show information about a provider",
        description="Show detailed information about a specific provider"
    )
    info_parser.add_argument(
        "provider",
        help="Name of the provider"
    )
    info_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    
    return parser


def providers_command(args: argparse.Namespace) -> int:
    """
    Execute the providers command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    import json
    
    if not hasattr(args, 'subcommand') or args.subcommand is None or args.subcommand == "list":
        return list_providers(args)
    elif args.subcommand == "use":
        return use_provider(args)
    elif args.subcommand == "info":
        return show_provider_info(args)
    else:
        print(f"Error: Unknown command '{getattr(args, 'subcommand', 'None')}'")
        return 1


def list_providers(args: argparse.Namespace) -> int:
    """List all providers"""
    import json
    
    providers = []
    
    for provider_name in registry.list():
        provider = registry.get(provider_name)
        if provider:
            info = provider.info
            authenticated = auth_manager.is_authenticated(provider_name)
            active = auth_manager.get_active_provider() == provider_name
            
            provider_data = {
                "name": provider_name,
                "display_name": info.display_name,
                "authenticated": authenticated,
                "active": active,
                "default_model": info.default_model,
                "capabilities": {k.value: v for k, v in info.supports.items()}
            }
            
            # Only include if authenticated filter is not set or if authenticated
            if not args.authenticated or authenticated:
                providers.append(provider_data)
    
    if args.json:
        print(json.dumps(providers, indent=2))
    else:
        print("Available providers:")
        print()
        
        if not providers:
            print("  No providers found")
            return 0
        
        # Sort by name
        providers.sort(key=lambda x: x["name"])
        
        for p in providers:
            auth_status = "✓" if p["authenticated"] else "✗"
            active_status = " [active]" if p["active"] else ""
            
            print(f"  {auth_status} {p['name']:15} {p['display_name']}{active_status}")
            print(f"      Default model: {p['default_model']}")
            print(f"      Capabilities: {', '.join([k for k, v in p['capabilities'].items() if v])}")
            print()
    
    return 0


def use_provider(args: argparse.Namespace) -> int:
    """Set the active provider"""
    if not args.provider:
        print("Error: Provider name is required")
        return 1
    
    if args.provider not in registry:
        print(f"Error: Provider '{args.provider}' not found")
        print("\nAvailable providers:")
        for provider_name in registry.list():
            print(f"  - {provider_name}")
        return 1
    
    if not auth_manager.is_authenticated(args.provider):
        print(f"Error: Not authenticated with {args.provider}")
        print(f"Run: kutti login {args.provider}")
        return 1
    
    try:
        auth_manager.set_active_provider(args.provider)
        print(f"✓ Active provider set to: {args.provider}")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def show_provider_info(args: argparse.Namespace) -> int:
    """Show information about a provider"""
    import json
    
    if not args.provider:
        print("Error: Provider name is required")
        return 1
    
    if args.provider not in registry:
        print(f"Error: Provider '{args.provider}' not found")
        return 1
    
    info = auth_manager.get_provider_info(args.provider)
    
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        if not info:
            print(f"Error: Could not get info for {args.provider}")
            return 1
        
        print(f"Provider: {info['name']}")
        print(f"Display Name: {info['display_name']}")
        print(f"Base URL: {info['base_url']}")
        print(f"Default Model: {info['default_model']}")
        print(f"Authenticated: {'Yes' if info['authenticated'] else 'No'}")
        print(f"Authentication Type: {info['authentication_type']}")
        
        if info.get('api_key_env_var'):
            print(f"Environment Variable: {info['api_key_env_var']}")
        
        print(f"\nCapabilities:")
        for cap, supported in info.get('supports', {}).items():
            status = "✓" if supported else "✗"
            print(f"  {status} {cap}")
    
    return 0


def main():
    """Main entry point for providers command"""
    parser = create_providers_parser()
    args = parser.parse_args()
    sys.exit(providers_command(args))


if __name__ == "__main__":
    main()
