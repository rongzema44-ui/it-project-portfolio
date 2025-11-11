"""
MainPage - Entry point for the Monash Merchant Online Supermarket System.

This module provides comprehensive functionality including user authentication,
registration, data management, and application navigation. It demonstrates key OOP
principles through abstraction of page interfaces, encapsulation of data operations,
and polymorphic page dispatch for different user roles.

Author: Applied10_Group6
Version: 3.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import re
import os
from AdminPage import AdminPage
from UserPage import UserPage
from InputHandler import InputHandler, BackToMainException, ExitApplicationException


# Abstract base class for all pages (Abstraction principle)
class Page(ABC):
    """
    Abstract base class for all page types.

    Demonstrates abstraction: defines interface that all pages must implement.
    """
    @abstractmethod
    def run(self) -> None:
        """Run the page - must be implemented by subclasses."""
        pass


class ScreenManager:
    """
    Abstract base class defining the interface for all page components.

    This class ensures that all page implementations provide a consistent
    interface for navigation and execution.
    """

    @staticmethod
    def clear_screen() -> None:
        """Clears the terminal screen in a cross-platform manner.

        This method detects the operating system and uses the appropriate
        command to clear the terminal display.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_separator(char: str = "=", length: int = 60) -> None:
        """Prints a separator line for visual formatting.

        :param char: Character to use for the separator line.
        :param length: Length of the separator line.
        """
        print(char * length)


class DataManager:
    """
    Handles data persistence operations for loading and saving application data.

    This class encapsulates file I/O operations with comprehensive error handling
    to ensure data integrity and provide meaningful error messages.
    """

    @staticmethod
    def load_data(filename: str) -> Dict[str, Any]:
        """
        Loads data from a JSON file with comprehensive error handling.

        :param filename: Path to the JSON file to load.
        :return: Dictionary containing the loaded data, or empty dictionary on error.
        """
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found, starting with empty data.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: {filename} is corrupted, starting with empty data.")
            return {}

    @staticmethod
    def save_data(filename: str, data: Dict[str, Any]) -> bool:
        """
        Saves data to a JSON file with error handling.

        :param filename: Path to the JSON file where data will be saved.
        :param data: Dictionary containing the data to save.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving to {filename}: {e}")
            return False


class InputValidator:
    """
    Provides input validation utilities for user data.

    This class encapsulates validation logic for various types of user input
    including email addresses and passwords.
    """

    # Email patterns as class constants
    MONASH_EMAIL_PATTERN = r'(.+@student\.monash\.edu|.+@monash\.edu)'

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validates that an email address matches Monash University format.

        :param email: The email address to validate.
        :return: True if the email matches Monash format, False otherwise.
        """
        return bool(re.match(InputValidator.MONASH_EMAIL_PATTERN, email))

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validates that a password meets security requirements.

        Requirements:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one number

        :param password: The password to validate.
        :return: True if the password meets all requirements, False otherwise.
        """
        return (len(password) >= 8 and
                bool(re.search(r'[A-Z]', password)) and
                bool(re.search(r'[0-9]', password)))

class MainPage(Page):
    """
    Main entry point for the Monash Merchant Online Supermarket System.

    This class manages the main menu, user authentication, registration,
    and coordinates the launch of specialized pages for different user types.
    """

    # Class constants for filenames
    USERS_FILE = 'users.txt'
    ADMINS_FILE = 'admins.txt'
    PRODUCTS_FILE = 'products.txt'
    ORDERS_FILE = 'orders.txt'
    CARTS_FILE = 'carts.txt'

    # Admin credentials as class constants
    ADMIN_EMAIL = 'admin@monash.edu'
    ADMIN_PASSWORD = 'Admin1234!'

    def __init__(self):
        """
        Constructs a MainPage instance and loads all core application data.

        This initializer loads user, admin, product, order, and cart data
        from their respective files to initialize the application state.
        """
        # Use private attributes for encapsulation
        self.__users = DataManager.load_data(self.USERS_FILE)
        self.__admins = DataManager.load_data(self.ADMINS_FILE)
        self.__products = DataManager.load_data(self.PRODUCTS_FILE)
        self.__orders = DataManager.load_data(self.ORDERS_FILE)
        self.__carts = DataManager.load_data(self.CARTS_FILE)

    # Property decorators for controlled access (Encapsulation)
    @property
    def users(self) -> Dict[str, Any]:
        """Retrieves the users dictionary.

        :return: Dictionary containing all user data.
        """
        return self.__users

    @property
    def products(self) -> Dict[str, Any]:
        """Retrieves the products dictionary.

        :return: Dictionary containing all product data.
        """
        return self.__products

    @property
    def orders(self) -> Dict[str, Any]:
        """Retrieves the orders dictionary.

        :return: Dictionary containing all order data.
        """
        return self.__orders

    @property
    def carts(self) -> Dict[str, Any]:
        """Retrieves the carts dictionary.

        :return: Dictionary containing all shopping cart data.
        """
        return self.__carts

    def save_all_data(self) -> None:
        """Saves all application data to their respective files.

        This method persists user, admin, product, order, and cart data
        to ensure data consistency across application sessions.
        """
        DataManager.save_data(self.USERS_FILE, self.__users)
        DataManager.save_data(self.ADMINS_FILE, self.__admins)
        DataManager.save_data(self.PRODUCTS_FILE, self.__products)
        DataManager.save_data(self.ORDERS_FILE, self.__orders)
        DataManager.save_data(self.CARTS_FILE, self.__carts)

    def run(self) -> None:
        """
        Executes the main application loop.

        This method implements the abstract run() method from the Page class
        and provides the primary user interaction flow for the main menu.
        """
        while True:
            try:
                ScreenManager.clear_screen()
                self.__display_main_menu()
                choice = InputHandler.get_choice(
                    "Enter your choice: ",
                    valid_choices=['1', '2', '3', '4'],
                    allow_main=False   # Already at main menu
                )

                if choice == '1':
                    self.handle_login()
                elif choice == '2':
                    #self.handle_register()
                    print("Temporarily disable registration for testing")
                    input("Press Enter to continue...")
                    pass
                elif choice == '3':
                    print("Exiting system...")
                    break
                elif choice == '4':
                    print("Running tests...")
                    print("Tests are currently disabled.")
                    input("Press Enter to continue...")
                    # self.__run_tests()  # Can be extended

            except ExitApplicationException as e:
                # Handle exit request
                InputHandler.handle_navigation_exception(e)
                break

    def __display_main_menu(self) -> None:
        """
        Displays the main menu options to the user.

        This private method handles the visual presentation of the main
        navigation menu with clear options for user interaction.
        """
        print("\n" + "="*60)
        print("  Welcome to Monash Merchant Online Supermarket System")
        print("="*60)
        print("1. Login")
        print("2. Register(Disabled for Testing)")
        print("3. Exit")
        print("4. Test")
        print("="*60)

    def handle_login(self) -> None:
        """
        Handles user authentication and login process.

        This method validates user credentials and launches the appropriate
        interface based on user type (admin or regular user).
        """
        email = input("Enter your Monash email: ").strip()
        password = input("Enter your password: ").strip()

        # Check admin credentials
        if self.__is_admin_login(email, password):
            print("Admin login successful.")
            self.__launch_admin_page(email)
            return

        # Check user credentials
        if self.__is_valid_user_login(email, password):
            print("Login successful.")
            self.__launch_user_page(email)
            return

        print("\n❌ Invalid email or password.")
        input("Press Enter to continue...")

    def __is_admin_login(self, email: str, password: str) -> bool:
        """
        Validates administrator login credentials.

        :param email: The email address to validate.
        :param password: The password to validate.
        :return: True if credentials match admin account, False otherwise.
        """
        return email == self.ADMIN_EMAIL and password == self.ADMIN_PASSWORD

    def __is_valid_user_login(self, email: str, password: str) -> bool:
        """
        Validates regular user login credentials.

        :param email: The email address to validate.
        :param password: The password to validate.
        :return: True if credentials match a registered user, False otherwise.
        """
        return (email in self.__users and
                self.__users[email].get('password') == password)

    def __launch_admin_page(self, admin_email: str = "admin@monash.edu") -> None:
        """
        Launch admin page with polymorphic dispatch.

        Polymorphism: Calls run() on Page interface.

        :param admin_email: Email address of the logged-in administrator.
        """
        page: Page = AdminPage(self.__products, admin_email)
        page.run()

    def __launch_user_page(self, email: str) -> None:
        """
        Launches the user interface for the specified user.

        :param email: The email address of the user to launch the interface for.
        """
        page: Page = UserPage(email, self.__users, self.__products)
        page.run()
        # Save data after user session
        DataManager.save_data(self.USERS_FILE, self.__users)
        DataManager.save_data(self.PRODUCTS_FILE, self.__products)


    def handle_register(self) -> None:
        """
        Handles new user registration with comprehensive validation.

        This method collects user information, validates input data,
        and creates a new user account if all validations pass.
        """
        # Collect and validate email
        email = input("Enter your Monash email: ").strip()
        if not InputValidator.validate_email(email):
            print("\n❌ Invalid Monash email format.")
            print("   Please use @student.monash.edu or @monash.edu email.")
            input("Press Enter to continue...")
            return

        if email in self.__users:
            print("\n❌ This email is already registered.")
            print("   Please login or use a different email.")
            input("Press Enter to continue...")
            return

        # Collect and validate password
        password = input("Enter your password: ").strip()
        if not InputValidator.validate_password(password):
            print("\n❌ Password must be at least 8 characters, with one uppercase letter and one number.")
            input("Press Enter to continue...")
            return

        # Collect user profile information
        user_profile = self.__collect_user_profile(email, password)

        # Register user
        self.__register_new_user(email, user_profile)

    def __collect_user_profile(self, email: str, password: str) -> Dict[str, Any]:
        """
        Collects comprehensive user profile information during registration.

        :param email: The user's email address.
        :param password: The user's password.
        :return: Dictionary containing the complete user profile.
        """
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        date_of_birth = input("Date of Birth (DD/MM/YYYY): ").strip()
        gender = input("Gender (Male, Female, Other): ").strip()
        mobile_number = input("Mobile Number: ").strip()
        address = input("Address: ").strip()

        return {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'gender': gender,
            'mobile_number': mobile_number,
            'address': address,
            'balance': 1000,
            'is_vip': False,
            'orders': [],
            'membership_history': []
        }

    def __register_new_user(self, email: str, user_profile: Dict[str, Any]) -> None:
        """
        Registers a new user account and persists the data.

        :param email: The email address for the new user account.
        :param user_profile: Dictionary containing the user's profile data.
        """
        self.__users[email] = user_profile
        DataManager.save_data(self.USERS_FILE, self.__users)
        print("Registration successful! You have been granted an initial $1000 credit.")


if __name__ == '__main__':
    """
    Application entry point.

    This block creates and runs the MainPage instance when the script
    is executed directly, serving as the starting point for the application.
    """
    app = MainPage()
    app.run()