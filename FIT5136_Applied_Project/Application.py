"""
Application.py - Main entry point for Monash Merchant Online Supermarket System

This is the primary entry point that initializes and runs the entire application.
It provides a clean separation between the application launcher and the main logic.

Usage:
    python Application.py

Author: Applied10_Group6
Version: 1.0
Date: 2025-10-12
"""

import sys
import os

# Add src directory to Python path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Change working directory to src for proper file access
os.chdir(src_dir)

from mainPage import MainPage


def print_welcome_banner():
    """Display welcome banner when application starts."""
    print("\n" + "="*70)
    print(" "*15 + "MONASH MERCHANT ONLINE SUPERMARKET")
    print(" "*20 + "Welcome to Our Shopping System")
    print("="*70)
    print("\n🛒 Your one-stop shop for all your needs!")
    print("🎓 Special benefits for Monash students")
    print("💎 VIP membership available with exclusive discounts")
    print("\n" + "="*70)
    input("\nPress Enter to continue...")


def main():
    """
    Main application entry point.

    Initializes the application and handles any startup errors.
    """
    try:
        # Display welcome banner
        print_welcome_banner()

        # Initialize and run the main application
        app = MainPage()
        app.run()

    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user.")
        print("Thank you for using Monash Merchant Online Supermarket!")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please contact system administrator for assistance.")
        sys.exit(1)

    finally:
        print("\n" + "="*70)
        print("Thank you for shopping with Monash Merchant!")
        print("Have a great day! 🌟")
        print("="*70 + "\n")


if __name__ == '__main__':
    main()
