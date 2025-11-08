#!/usr/bin/env python3
"""
Minimal entry point for the Hackaton project.
Run: python -m src.main
"""
import os


def main() -> None:
    """Simple main function used as an entry point."""
    print("Hackaton: starting src.main")
    debug = os.getenv("DEBUG", "false")
    print(f"DEBUG={debug}")
    # Placeholder for project startup logic
    print("Hello, Hackaton!")


if __name__ == "__main__":
    main()
