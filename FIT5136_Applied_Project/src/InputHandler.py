"""
InputHandler - Global input handler with menu navigation controls.

This module provides centralized input handling with special commands that
allow users to navigate to main menu or exit at any time. It implements
exception-based navigation control for cleaner code flow and better separation
of concerns.

Special Navigation Commands:
- 'main' or 'm' - Return to main menu (raises BackToMainException)
- 'exit', 'quit', or 'q' - Exit application (raises ExitApplicationException)

Author: Applied10_Group6
Version: 2.0
"""

import sys
from typing import Optional


class NavigationException(Exception):
    """
    NavigationException - Base exception for navigation control.

    This base class provides a common type for all navigation-related
    exceptions, enabling centralized exception handling for user navigation
    actions throughout the application.

    """
    pass


class BackToMainException(NavigationException):
    """
    BackToMainException - Exception to signal return to main menu.

    This exception is raised when the user enters a command to navigate
    back to the main menu. It allows clean navigation control without
    complex return value checking.

    """
    pass


class ExitApplicationException(NavigationException):
    """
    ExitApplicationException - Exception to signal application exit.

    This exception is raised when the user confirms they want to exit
    the application. It triggers graceful shutdown procedures.

    """
    pass


class InputHandler:
    """
    InputHandler - Centralized input handler with navigation controls.

    This class provides static methods for handling user input with built-in
    support for navigation commands. It allows users to enter special commands
    at any input prompt to navigate through the application or exit gracefully.

    Supported Navigation Commands:
    - 'main', 'm' - Return to main menu (raises BackToMainException)
    - 'exit', 'quit', 'q' - Exit application (raises ExitApplicationException)

    """

    # Special command keywords
    MAIN_COMMANDS = ['main', 'm']
    EXIT_COMMANDS = ['exit', 'quit', 'q']

    # Help text
    HELP_TEXT = """
💡 Navigation Commands (available anytime):
   • Type 'main' or 'm' - Return to main menu
   • Type 'exit' or 'q' - Exit application
"""

    @staticmethod
    def get_input(prompt: str, allow_main: bool = True, allow_exit: bool = True) -> str:
        """
        Gets user input with navigation control support.

        This method displays a prompt, accepts user input, and processes
        navigation commands. It automatically adds a help hint to prompts
        and handles the '?' command to display navigation help.

        :param prompt: The prompt message to display to the user.
        :param allow_main: Whether to allow 'main' command (default: True).
        :param allow_exit: Whether to allow 'exit' command (default: True).
        :return: The user's input string (lowercased and trimmed).
        :raises BackToMainException: If user enters 'main' or 'm' and allowed.
        :raises ExitApplicationException: If user enters 'exit', 'quit', or 'q' and confirms.
        """
        # Add hint to prompt
        hint = " (type '?' for help)"
        if hint not in prompt:
            prompt = prompt.rstrip() + hint + ": " if prompt.endswith(":") else prompt + hint

        user_input = input(prompt).strip().lower()

        # Handle help request
        if user_input == '?':
            print(InputHandler.HELP_TEXT)
            return InputHandler.get_input(prompt, allow_main, allow_exit)

        # Handle navigation commands
        if allow_main and user_input in InputHandler.MAIN_COMMANDS:
            raise BackToMainException("User requested main menu")

        if allow_exit and user_input in InputHandler.EXIT_COMMANDS:
            confirm = input("Are you sure you want to exit? (y/n): ").strip().lower()
            if confirm == 'y':
                raise ExitApplicationException("User requested exit")
            else:
                return InputHandler.get_input(prompt, allow_main, allow_exit)

        return user_input

    @staticmethod
    def get_choice(prompt: str, valid_choices: list = None,
                   allow_main: bool = True, allow_exit: bool = True) -> str:
        """
        Gets user choice with validation and navigation support.

        This method repeatedly prompts the user until they provide a valid
        choice from the specified list. It integrates navigation control
        and input validation in a single method.

        :param prompt: The prompt message to display.
        :param valid_choices: List of valid choices (strings or convertible to strings).
                             If None, any input is accepted.
        :param allow_main: Whether to allow 'main' command (default: True).
        :param allow_exit: Whether to allow 'exit' command (default: True).
        :return: A valid user choice from the provided list.
        :raises BackToMainException: If user enters 'main' or 'm' and allowed.
        :raises ExitApplicationException: If user enters 'exit', 'quit', or 'q' and confirms.
        """
        while True:
            try:
                choice = InputHandler.get_input(prompt, allow_main, allow_exit)

                # If no validation needed, return choice
                if valid_choices is None:
                    return choice

                # Validate choice
                if choice in valid_choices or choice in [str(c) for c in valid_choices]:
                    return choice
                else:
                    print(f"❌ Invalid choice. Please enter one of: {', '.join(map(str, valid_choices))}")

            except NavigationException:
                # Re-raise navigation exceptions
                raise

    @staticmethod
    def show_help():
        """
        Displays navigation help information.

        This method prints the help text that explains available navigation
        commands to the user.

        :return: None
        """
        print(InputHandler.HELP_TEXT)

    @staticmethod
    def handle_navigation_exception(e: NavigationException, context: str = ""):
        """
        Handles navigation exceptions with appropriate messages.

        This method provides centralized handling for navigation exceptions,
        displaying appropriate messages to the user and performing necessary
        actions (such as exiting the application).

        :param e: The navigation exception to handle.
        :param context: Optional context information for logging purposes.
        :return: None
        """
        if isinstance(e, BackToMainException):
            print("🏠 Returning to main menu...")
        elif isinstance(e, ExitApplicationException):
            print("\n" + "="*60)
            print("Thank you for using Monash Merchant Online Supermarket!")
            print("Have a great day! 🌟")
            print("="*60)
            sys.exit(0)


# Convenience functions for quick access
def get_input(prompt: str, **kwargs) -> str:
    """
    Convenience wrapper for InputHandler.get_input().

    This function provides module-level access to the InputHandler's
    get_input method for simplified usage.

    :param prompt: The prompt message to display.
    :param kwargs: Additional keyword arguments passed to InputHandler.get_input().
    :return: User input string.
    :raises BackToMainException: If user navigates to main menu.
    :raises ExitApplicationException: If user exits application.
    """
    return InputHandler.get_input(prompt, **kwargs)


def get_choice(prompt: str, valid_choices: list = None, **kwargs) -> str:
    """
    Convenience wrapper for InputHandler.get_choice().

    This function provides module-level access to the InputHandler's
    get_choice method for simplified usage.

    :param prompt: The prompt message to display.
    :param valid_choices: List of valid choices.
    :param kwargs: Additional keyword arguments passed to InputHandler.get_choice().
    :return: Valid user choice.
    :raises BackToMainException: If user navigates to main menu.
    :raises ExitApplicationException: If user exits application.
    """
    return InputHandler.get_choice(prompt, valid_choices, **kwargs)


if __name__ == '__main__':
    # Demo usage
    print("InputHandler Demo")
    print("="*60)
    InputHandler.show_help()

    try:
        name = InputHandler.get_input("Enter your name: ")
        print(f"Hello, {name}!")

        choice = InputHandler.get_choice("Choose option (1-3): ", ['1', '2', '3'])
        print(f"You chose: {choice}")

    except BackToMainException:
        print("Going to main menu...")
    except ExitApplicationException:
        print("Exiting...")
