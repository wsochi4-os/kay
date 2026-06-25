"""
CLI Session Command

kutti session
"""

import argparse
import sys
import json
from typing import Optional

from auth.manager import auth_manager


def create_session_parser(parser: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    """
    Create the session command parser.
    
    Args:
        parser: Parent parser (optional)
        
    Returns:
        Argument parser for session command
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Show session information")
    else:
        parser = parser.add_parser(
            "session",
            help="Show session information",
            description="Show information about the current session and authentication state"
        )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--provider", "-p",
        help="Show session for a specific provider"
    )
    
    return parser


def session_command(args: argparse.Namespace) -> int:
    """
    Execute the session command.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    if args.provider:
        session = auth_manager.get_session(args.provider)
        if not session:
            print(f"Error: No session found for {args.provider}")
            return 1
    else:
        session = auth_manager.get_active_session()
        if not session:
            print("No active session")
            print("\nRun 'kutti login <provider>' to authenticate")
            return 0
    
    if args.json:
        print(json.dumps(session, indent=2))
    else:
        print("Session Information:")
        print()
        
        for key, value in session.items():
            if isinstance(value, float):
                # Convert timestamp to readable format
                import datetime
                value = datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {key}: {value}")
    
    return 0


def main():
    """Main entry point for session command"""
    parser = create_session_parser()
    args = parser.parse_args()
    sys.exit(session_command(args))


if __name__ == "__main__":
    main()
