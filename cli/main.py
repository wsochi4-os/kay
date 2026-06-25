#!/usr/bin/env python3
"""
Kutti CLI - Main Entry Point

OpenCode-compatible authentication & provider system for Kutti.

Usage:
    kutti login PROVIDER
    kutti logout PROVIDER
    kutti providers list
    kutti provider use PROVIDER
    kutti models list
    kutti models refresh
    kutti session
"""

import argparse
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.login import create_login_parser, login_command
from cli.logout import create_logout_parser, logout_command
from cli.providers import create_providers_parser, providers_command
from cli.models import create_models_parser, models_command
from cli.session import create_session_parser, session_command


def create_main_parser() -> argparse.ArgumentParser:
    """Create the main CLI parser"""
    parser = argparse.ArgumentParser(
        prog="kutti",
        description="Kutti - Your Personal AI CLI Agent (OpenCode-compatible)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kutti login openai                    # Login to OpenAI
  kutti login groq --api-key KEY        # Login with API key
  kutti logout openai                   # Logout from OpenAI
  kutti providers list                  # List all providers
  kutti provider use groq               # Set active provider
  kutti models list                     # List available models
  kutti models refresh                  # Refresh model list
  kutti session                         # Show session info
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Login command
    login_parser = create_login_parser(subparsers)
    
    # Logout command
    logout_parser = create_logout_parser(subparsers)
    
    # Providers command
    providers_parser = create_providers_parser(subparsers)
    
    # Models command
    models_parser = create_models_parser(subparsers)
    
    # Session command
    session_parser = create_session_parser(subparsers)
    
    # Auth status command (alias for session)
    subparsers.add_parser(
        "auth",
        help="Show authentication status",
        description="Show authentication status (alias for session)"
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_main_parser()
    args = parser.parse_args()
    
    # Handle auth command (alias for session)
    if hasattr(args, 'command') and args.command == 'auth':
        # Convert to session command
        args.command = 'session'
    
    # Route to appropriate command handler
    if hasattr(args, 'command'):
        if args.command == 'login':
            sys.exit(login_command(args))
        elif args.command == 'logout':
            sys.exit(logout_command(args))
        elif args.command == 'providers':
            sys.exit(providers_command(args))
        elif args.command == 'models':
            sys.exit(models_command(args))
        elif args.command == 'session':
            sys.exit(session_command(args))
        else:
            parser.print_help()
            sys.exit(1)
    else:
        # No command specified, show help
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
