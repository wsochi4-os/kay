"""
CLI Logout Command

kutti logout PROVIDER
"""

import argparse
import sys
from typing import Optional

from providers.registry import registry
from auth.manager import auth_manager


def create_logout_parser(parser: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    """
    Create the logout command parser.
    
    Args:
        parser: Parent parser (optional)
        
    Returns:
        Argument parser for logout command
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Logout from an AI provider")
    else:
        parser = parser.add_parser(
            "logout",
            help="Logout from an AI provider",
            description="Logout from an AI provider and clear stored credentials"
        )
    
    parser.add_argument(
        "provider",
        nargs="?",
        help="Name of the provider to logout from (optional, defaults to all)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Logout from all providers"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force logout without confirmation"
    )
    
    return parser


def logout_command(args: argparse.Namespace) -> int:
    """
    Execute the logout command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    import asyncio
    
    # Determine which providers to logout from
    providers_to_logout = []
    
    if args.all:
        providers_to_logout = registry.list()
    elif args.provider:
        if args.provider not in registry:
            print(f"Error: Provider '{args.provider}' not found")
            return 1
        providers_to_logout = [args.provider]
    else:
        # Default to active provider
        active = auth_manager.get_active_provider()
        if active:
            providers_to_logout = [active]
        else:
            print("Error: No active provider to logout from")
            print("Usage: kutti logout [PROVIDER] [--all]")
            return 1
    
    # Confirm if not forced
    if not args.force and not args.all:
        print(f"Are you sure you want to logout from {', '.join(providers_to_logout)}? [y/N]")
        try:
            response = input().strip().lower()
            if response not in ('y', 'yes'):
                print("Logout cancelled")
                return 0
        except (EOFError, KeyboardInterrupt):
            print("\nLogout cancelled")
            return 0
    
    # Perform logout
    if args.all:
        print("Logging out from all providers...")
    else:
        print(f"Logging out from {', '.join(providers_to_logout)}...")
    
    try:
        for provider_name in providers_to_logout:
            if args.all:
                success = asyncio.run(auth_manager.logout(provider_name))
            else:
                import asyncio
                success = asyncio.run(auth_manager.logout(provider_name))
            
            if success:
                print(f"  ✓ Logged out from {provider_name}")
            else:
                print(f"  ✗ Failed to logout from {provider_name}")
        
        # Clear active provider if we logged out from it
        active = auth_manager.get_active_provider()
        if active in providers_to_logout:
            auth_manager.set_active_provider(None)
            print(f"  Cleared active provider")
        
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def main():
    """Main entry point for logout command"""
    parser = create_logout_parser()
    args = parser.parse_args()
    sys.exit(logout_command(args))


if __name__ == "__main__":
    main()
