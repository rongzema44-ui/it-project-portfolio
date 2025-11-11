"""
UserPage Module
Represents the main customer interface for the Monash Online Supermarket system.

This module encapsulates all customer-side functionalities, including product browsing,
cart management, checkout, profile editing, funds top-up, and VIP membership operations.
It also integrates with external components such as the ShoppingPage and InputHandler
for a complete interactive experience.

Author: Tao Pan
Version: 3.0
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from collections import OrderedDict
import os
from ShoppingPage import Shopping
from InputHandler import InputHandler, BackToMainException, ExitApplicationException


class Page(ABC):
    """
    Page - Abstract base class defining the interface for all page classes.

    This class enforces a consistent structure across all system pages by requiring
    the implementation of a run() method in each subclass.
    """

    @abstractmethod
    def run(self) -> None:
        """
        Runs the logic of the page.

        :return: None
        """
        pass


class ScreenManager:
    """
    ScreenManager - Provides screen control utilities for the system.

    This class offers methods to clear the terminal screen across different operating systems.
    """

    @staticmethod
    def clear_screen() -> None:
        """
        Clears the terminal screen.

        :return: None
        """
        os.system('cls' if os.name == 'nt' else 'clear')


class VIPManager:
    """
    VIPManager - Manages all VIP-related operations.

    This class provides methods to activate, renew, and cancel VIP memberships,
    as well as to calculate membership costs and handle Monash student discounts.
    """

    STANDARD_VIP_COST = 20.0
    MONASH_STUDENT_DISCOUNT = 0.10

    @staticmethod
    def is_monash_student(email: str) -> bool:
        """
        Checks if the user is a Monash student.

        :param email: The user's email address.
        :return: True if the email belongs to a Monash student, otherwise False.
        """
        return '@student.monash.edu' in email.lower()

    @staticmethod
    def calculate_vip_cost(email: str, years: int = 1) -> float:
        """
        Calculates the VIP membership cost, applying discount for Monash students.

        :param email: The user's email address.
        :param years: The number of years to purchase.
        :return: The total VIP cost after discounts.
        """
        base_cost = VIPManager.STANDARD_VIP_COST * years
        if VIPManager.is_monash_student(email):
            discount = base_cost * VIPManager.MONASH_STUDENT_DISCOUNT
            return base_cost - discount
        return base_cost

    @staticmethod
    def activate_vip(user: Dict[str, Any], years: int, cost: float) -> None:
        """
        Activates or extends VIP membership for a user.

        :param user: The user's data dictionary.
        :param years: The number of years to extend.
        :param cost: The total membership cost.
        :return: None
        """
        user['is_vip'] = True
        current_date = datetime.now()
        expiry_date = datetime(current_date.year + years, current_date.month, current_date.day)
        user['vip_expiry'] = expiry_date.strftime("%Y-%m-%d")
        user['membership_history'].append({
            'date': current_date.strftime("%Y-%m-%d %H:%M:%S"),
            'cost': cost,
            'years': years,
            'type': 'VIP Purchase'
        })

    @staticmethod
    def cancel_vip(user: Dict[str, Any]) -> bool:
        """
        Cancels the user's VIP membership without refund.

        :param user: The user's data dictionary.
        :return: True if successfully cancelled, False otherwise.
        """
        if not user.get('is_vip', False):
            return False
        user['is_vip'] = False
        user['membership_history'].append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cost': 0,
            'type': 'VIP Cancelled (no refund)'
        })
        return True

    @staticmethod
    def check_vip_expiry(user: Dict[str, Any]) -> bool:
        """
        Checks and deactivates expired VIP memberships.

        :param user: The user's data dictionary.
        :return: True if VIP has expired, False otherwise.
        """
        if not user.get('is_vip', False):
            return False
        expiry_str = user.get('vip_expiry')
        if not expiry_str:
            return False
        try:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            if datetime.now() > expiry_date:
                user['is_vip'] = False
                return True
        except ValueError:
            pass
        return False


class UserPage(Page):
    """
    UserPage - Represents the customer-facing interface of the system.

    This class allows customers to browse products, manage their carts, checkout,
    edit profiles, top up funds, and handle VIP membership activities.
    """

    def __init__(self, user_email: str, users_data: Dict[str, Any], products_data: Dict[str, Any]):
        """
        Constructs a UserPage with user and product data.

        :param user_email: The logged-in user's email address.
        :param users_data: A dictionary containing all users' data.
        :param products_data: A dictionary containing all products' data.
        """
        self.__user_email = user_email
        self.__users = users_data
        self.__products = products_data
        self.__cart: OrderedDict = OrderedDict()
        VIPManager.check_vip_expiry(self.__users[self.__user_email])

    def run(self) -> None:
        """
        Runs the main user interaction loop.

        :return: None
        """
        while True:
            try:
                ScreenManager.clear_screen()
                self.__display_menu()
                choice = InputHandler.get_choice(
                    "Enter your choice (1-10): ",
                    valid_choices=[str(i) for i in range(1, 11)],
                    allow_main=True
                )
                if not self.__handle_menu_choice(choice):
                    break
            except BackToMainException:
                print("\nReturning to main menu...")
                input("Press Enter to continue...")
                break
            except ExitApplicationException as e:
                InputHandler.handle_navigation_exception(e)
                break

    def __display_menu(self) -> None:
        """
        Displays the main user operations menu.

        :return: None
        """
        user = self.__users[self.__user_email]
        vip_status = "Yes" if user.get('is_vip', False) else "No"
        print("\n" + "=" * 60)
        print(f"Balance: ${user['balance']:.2f} | VIP: {vip_status}")
        print("=" * 60)
        print("1. Browse Products")
        print("2. View Cart")
        print("3. Checkout")
        print("4. View Profile")
        print("5. Edit Profile")
        print("6. Top Up Funds")
        print("7. Purchase VIP Membership")
        print("8. View Order History")
        print("9. VIP Options")
        print("10. Logout")
        print("=" * 60)

    def __handle_menu_choice(self, choice: str) -> bool:
        """
        Executes the selected operation from the main menu.

        :param choice: The user's selected menu option.
        :return: False if user logs out, otherwise True.
        """
        menu_actions = {
            '1': self.browse_products,
            '2': self.view_cart,
            '3': self.checkout,
            '4': self.view_profile,
            '5': self.__edit_profile,
            '6': self.top_up,
            '7': self.purchase_vip,
            '8': self.view_order_history,
            '9': self.__update_vip_status
        }
        if choice == '10':
            self.__cart.clear()
            print("Logging out... Your cart has been cleared.")
            input("\nPress Enter to continue...")
            return False
        elif choice in menu_actions:
            menu_actions[choice]()
            return True
        else:
            print("Invalid input. Please enter 1–10.")
            return True

    def browse_products(self) -> None:
        """
        Opens the product browsing page for the user.

        :return: None
        """
        shopping_page = Shopping(self.__products, self.__user_email, self.__users, self.__cart)
        shopping_page.browse()
        self.__cart = shopping_page.get_cart()

    def view_cart(self) -> None:
        """
        Displays the shopping cart contents and allows modification.

        :return: None
        """
        shopping_page = Shopping(self.__products, self.__user_email, self.__users, self.__cart)
        shopping_page.view_cart()
        if self.__cart:
            shopping_page.cart_actions()
        else:
            print("\nYour cart is empty.")
            input("\nPress Enter to continue...")
        self.__cart = shopping_page.get_cart()
        self.__users = shopping_page.get_users()
        self.__products = shopping_page.get_products()
        self.__save_data()

    def checkout(self) -> None:
        """
        Handles checkout process and updates user and inventory data.

        :return: None
        """
        shopping_page = Shopping(self.__products, self.__user_email, self.__users, self.__cart)
        shopping_page.checkout()
        self.__cart = shopping_page.get_cart()
        self.__users = shopping_page.get_users()
        self.__products = shopping_page.get_products()
        self.__save_data()

    def view_profile(self) -> None:
        """
        Displays user profile information.

        :return: None
        """
        user = self.__users[self.__user_email]
        print("\n--- My Profile ---")
        print(f"Email: {self.__user_email}")
        print(f"Name: {user.get('first_name', '')} {user.get('last_name', '')}")
        print(f"Mobile: {user.get('mobile_number', 'N/A')}")
        print(f"Address: {user.get('address', 'N/A')}")
        print(f"Balance: ${user.get('balance', 0):.2f}")
        print(f"VIP: {'Yes' if user.get('is_vip', False) else 'No'}")
        input("\nPress Enter to continue...")

    def top_up(self) -> None:
        """
        Allows the user to top up their balance.

        :return: None
        """
        try:
            amount = float(input("Enter amount to top up (max $1000): "))
            if 0 < amount <= 1000:
                self.__users[self.__user_email]['balance'] += amount
                self.__save_data()
                print(f"Successfully topped up ${amount:.2f}.")
            else:
                print("Invalid amount. Please enter a value between 0 and 1000.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
        input("\nPress Enter to continue...")

    def purchase_vip(self) -> None:
        """
        Allows the user to purchase or extend VIP membership.

        :return: None
        """
        user = self.__users[self.__user_email]
        print("--- VIP Membership ---")
        years = self.__get_vip_years()
        if not years:
            return
        cost = VIPManager.calculate_vip_cost(self.__user_email, years)
        if user['balance'] < cost:
            print("Insufficient balance. Please top up first.")
            input("\nPress Enter to continue...")
            return
        confirm = input(f"Confirm purchase for ${cost:.2f}? (y/n): ").lower()
        if confirm != 'y':
            print("Purchase cancelled.")
            input("\nPress Enter to continue...")
            return
        user['balance'] -= cost
        VIPManager.activate_vip(user, years, cost)
        self.__save_data()
        print(f"VIP activated until {user['vip_expiry']}.")
        input("\nPress Enter to continue...")

    def __get_vip_years(self) -> Optional[int]:
        """
        Prompts the user for the number of VIP membership years to purchase.

        :return: The number of years (1–5) or None if invalid.
        """
        try:
            years = int(input("Enter number of years (1–5): "))
            if 1 <= years <= 5:
                return years
            print("Please enter a number between 1 and 5.")
            return None
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
            return None

    def __update_vip_status(self) -> None:
        """
        Displays VIP options and allows cancellation or status viewing.

        :return: None
        """
        user = self.__users[self.__user_email]
        print(f"Current VIP: {'Yes' if user.get('is_vip', False) else 'No'}")
        print("1. Cancel VIP")
        print("2. View VIP Info")
        print("3. Back")
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            if VIPManager.cancel_vip(user):
                self.__save_data()
                print("VIP cancelled.")
            else:
                print("You are not a VIP.")
            input("\nPress Enter to continue...")
        elif choice == '2':
            self.__display_vip_info(user)
            input("\nPress Enter to continue...")

    def __display_vip_info(self, user: Dict[str, Any]) -> None:
        """
        Displays VIP expiry date and available benefits.

        :param user: The user's data dictionary.
        :return: None
        """
        if user.get('is_vip', False):
            print(f"VIP Expiry: {user.get('vip_expiry', 'N/A')}")
            print("Benefits: Access to special prices and discounts.")
        else:
            print("You are not currently a VIP member.")

    def __edit_profile(self) -> None:
        """
        Allows the user to edit their mobile number and address.

        :return: None
        """
        user = self.__users[self.__user_email]
        print("\n--- Edit Profile ---")
        print("1. Update Mobile")
        print("2. Update Address")
        print("3. Both")
        print("4. Back")
        choice = input("Enter your choice (1–4): ").strip()
        if choice == '1':
            user['mobile_number'] = input("Enter new mobile: ").strip()
        elif choice == '2':
            user['address'] = input("Enter new address: ").strip()
        elif choice == '3':
            user['mobile_number'] = input("Enter new mobile: ").strip()
            user['address'] = input("Enter new address: ").strip()
        self.__save_data()
        print("Profile updated successfully.")
        input("\nPress Enter to continue...")

    def view_order_history(self) -> None:
        """
        Displays the user's order and VIP membership history.

        This method loads orders from the Order system and displays them
        along with VIP membership history.

        :return: None
        """
        user = self.__users[self.__user_email]

        # Load orders from Order system
        print("\n" + "="*60)
        print("  📦 ORDER HISTORY")
        print("="*60)

        try:
            from Order import Order as OrderManager
            order_manager = OrderManager()
            user_orders = order_manager.list_orders(self.__user_email)

            if not user_orders:
                print("\nNo orders found.")
            else:
                print(f"\nTotal Orders: {len(user_orders)}\n")
                for order in user_orders:
                    print(f"Order ID: {order.order_id}")
                    print(f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Status: {order.status.value}")
                    print(f"Total: ${order.total_price:.2f}")
                    print(f"Items: {len(order.product_list)} product(s)")
                    print("-" * 60)
        except Exception as e:
            print(f"\n⚠️  Error loading orders: {e}")
            print("\nFalling back to legacy order data...")
            # Fallback: try to load from user's orders field
            if not user.get('orders'):
                print("No orders found.")
            else:
                for order in user['orders']:
                    print(f"Order ID: {order.get('id', 'N/A')} | Date: {order.get('date', 'N/A')} | Total: ${order.get('total_price', 0):.2f}")

        # Display membership history
        print("\n" + "="*60)
        print("  👑 MEMBERSHIP HISTORY")
        print("="*60)
        if not user.get('membership_history'):
            print("\nNo membership records found.")
        else:
            for record in user['membership_history']:
                print(f"{record['date']} - ${record['cost']:.2f} ({record['type']})")

        input("\nPress Enter to continue...")

    def __save_data(self) -> None:
        """
        Saves all user and product data.

        :return: None
        """
        from mainPage import DataManager
        DataManager.save_data('users.txt', self.__users)
        DataManager.save_data('products.txt', self.__products)