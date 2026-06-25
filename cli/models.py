"""
CLI Models Command

kutti models list
kutti models refresh
"""

import argparse
import sys
from typing import Optional

from models.registry import model_registry
from auth.manager import auth_manager
from providers.registry import registry


def create_models_parser(parser: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    """
    Create the models command parser.
    
    Args:
        parser: Parent parser (optional)
        
    Returns:
        Argument parser for models command
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Manage AI models")
    else:
        parser = parser.add_parser(
            "models",
            help="Manage AI models",
            description="List and manage AI models from all providers"
        )
    
    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available models",
        description="List all available models from all providers"
    )
    list_parser.add_argument(
        "--provider", "-p",
        help="Filter by provider"
    )
    list_parser.add_argument(
        "--search", "-s",
        help="Search for models by name or ID"
    )
    list_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    list_parser.add_argument(
        "--refresh", "-r",
        action="store_true",
        help="Refresh model list before displaying"
    )
    
    # Refresh command
    refresh_parser = subparsers.add_parser(
        "refresh",
        help="Refresh model list",
        description="Refresh the list of available models from all providers"
    )
    refresh_parser.add_argument(
        "--provider", "-p",
        help="Refresh models for a specific provider only"
    )
    refresh_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force refresh even if cache is still valid"
    )
    
    return parser


def models_command(args: argparse.Namespace) -> int:
    """
    Execute the models command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    import asyncio
    import json
    
    if not hasattr(args, 'subcommand') or args.subcommand is None or args.subcommand == "list":
        return list_models(args)
    elif args.subcommand == "refresh":
        return refresh_models(args)
    else:
        print(f"Error: Unknown command '{getattr(args, 'subcommand', 'None')}'")
        return 1


def list_models(args: argparse.Namespace) -> int:
    """List available models"""
    import asyncio
    import json
    
    # Refresh if requested
    if args.refresh:
        asyncio.run(model_registry.refresh(force=True))
    
    # Get models
    if args.provider:
        if args.provider not in registry:
            print(f"Error: Provider '{args.provider}' not found")
            return 1
        models = model_registry.get_models_by_provider(args.provider)
    elif args.search:
        models = model_registry.search_models(args.search)
    else:
        models = model_registry.list_all_models()
    
    if args.json:
        models_dict = [model.__dict__ for model in models]
        print(json.dumps(models_dict, indent=2))
    else:
        if not models:
            print("No models found")
            if args.provider:
                print(f"Provider '{args.provider}' may not have any models or may not be authenticated")
            return 0
        
        print("Available models:")
        print()
        
        # Sort by provider then by model ID
        models.sort(key=lambda x: (x.provider, x.id))
        
        current_provider = None
        for model in models:
            if model.provider != current_provider:
                current_provider = model.provider
                print(f"\n{current_provider}:")
            
            # Truncate long model IDs
            display_id = model.id
            if len(display_id) > 40:
                display_id = display_id[:37] + "..."
            
            print(f"  {display_id:40} {model.name}")
            if model.context_length > 0:
                print(f"    Context length: {model.context_length:,}")
            if model.description:
                print(f"    Description: {model.description[:60]}...")
        
        print(f"\nTotal: {len(models)} models")
    
    return 0


def refresh_models(args: argparse.Namespace) -> int:
    """Refresh model list"""
    import asyncio
    
    if args.provider:
        if args.provider not in registry:
            print(f"Error: Provider '{args.provider}' not found")
            return 1
        
        print(f"Refreshing models for {args.provider}...")
        count = asyncio.run(model_registry.refresh_provider(args.provider))
        print(f"✓ Refreshed {count} models from {args.provider}")
    else:
        print("Refreshing models from all providers...")
        count = asyncio.run(model_registry.refresh(force=args.force))
        print(f"✓ Refreshed {count} models from all providers")
    
    return 0


def main():
    """Main entry point for models command"""
    parser = create_models_parser()
    args = parser.parse_args()
    sys.exit(models_command(args))


if __name__ == "__main__":
    main()
