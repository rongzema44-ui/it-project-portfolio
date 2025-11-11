"""
AdminPage Module - Administrator interface for comprehensive system management.

This module provides administrator functionality for managing products, promotions,
and promotional codes. It demonstrates key OOP principles through encapsulation of
administrative logic, abstraction of management operations, and inheritance from
base page classes.

Author: Applied10_Group6
Version: 1.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from product import Product
import json
import os
from InputHandler import InputHandler, BackToMainException, ExitApplicationException


class Page(ABC):
    """
    Page - Abstract base class defining the interface for all page components.

    This class ensures that all page implementations provide a consistent
    interface for navigation and execution.

    """
    @abstractmethod
    def run(self) -> None:
        """
        Executes the main functionality of the page.

        This method must be implemented by all concrete page classes to define
        their specific behavior and user interaction flow.
        """
        pass


class ScreenManager:
    """
    ScreenManager - Utility class for managing terminal screen operations.

    This class provides static methods for screen management tasks such as
    clearing the terminal display in a cross-platform manner.

    """

    @staticmethod
    def clear_screen() -> None:
        """
        Clears the terminal screen in a cross-platform manner.

        This method detects the operating system and uses the appropriate
        command to clear the terminal display.
        """
        os.system('cls' if os.name == 'nt' else 'clear')


class ProductManager:
    """
    ProductManager - Encapsulates product management operations for administrators.

    This class centralizes all product-related business logic including display,
    validation, stock management, and filtering. It demonstrates the Single
    Responsibility Principle by focusing solely on product operations.

    """

    LOW_STOCK_DEFAULT_THRESHOLD = 5

    @staticmethod
    def display_product_list(products: Dict[str, Any], title: str = "All Products") -> None:
        """
        Displays a formatted list of products with in-stock items first.

        This method organizes products by stock status, showing available items
        before out-of-stock items for better user experience.

        :param products: Dictionary mapping product IDs to product information.
        :param title: Display title for the product list.
        """
        if not products:
            print("No products in the system.")
            return

        print(f"\n--- {title} ---")
        in_stock, out_of_stock = ProductManager._separate_by_stock(products)

        for product_id, product in in_stock + out_of_stock:
            ProductManager._display_single_product(product_id, product)

    @staticmethod
    def _separate_by_stock(products: Dict[str, Any]) -> Tuple[List[Tuple], List[Tuple]]:
        """
        Separates products into in-stock and out-of-stock lists.

        This private helper method organizes products by availability status
        for improved display organization.

        :param products: Dictionary of product data.
        :return: Tuple containing (in_stock_list, out_of_stock_list).
        """
        in_stock = []
        out_of_stock = []

        for product_id, product in products.items():
            if product.get('quantity', 0) > 0:
                in_stock.append((product_id, product))
            else:
                out_of_stock.append((product_id, product))

        return in_stock, out_of_stock

    @staticmethod
    def _display_single_product(product_id: str, product: Dict[str, Any]) -> None:
        """
        Displays detailed information for a single product.

        This private helper method formats and prints all product attributes,
        including food-specific fields when applicable.

        :param product_id: The unique identifier of the product.
        :param product: Dictionary containing product information.
        """
        print(f"ID: {product_id}")
        print(f"  Name: {product['name']}")
        print(f"  Brand: {product['brand']}")
        print(f"  Category: {product['category']}")
        print(f"  Price: ${product['price']}")
        print(f"  Member Price: ${product.get('member_price', 'N/A')}")
        print(f"  Quantity: {product['quantity']}")

        # Display food-specific information
        if product['category'].lower() == 'food':
            print(f"  Expiration Date: {product.get('expiration_date', 'N/A')}")
            print(f"  Ingredients: {product.get('ingredients', 'N/A')}")
            print(f"  Allergens: {product.get('allergens', 'None')}")

        if product.get('quantity', 0) == 0:
            print("  Status: OUT OF STOCK")

        print("-" * 20)

    @staticmethod
    def get_low_stock_products(products: Dict[str, Any], threshold: int) -> Dict[str, Any]:
        """
        Filters and returns products with stock levels at or below the threshold.

        This method helps administrators identify products that need restocking
        by filtering items based on inventory levels.

        :param products: Dictionary of all product data.
        :param threshold: Maximum stock level to include in results.
        :return: Dictionary containing only low-stock products.
        """
        return {
            pid: p for pid, p in products.items()
            if 'quantity' in p and p['quantity'] <= threshold
        }

    @staticmethod
    def validate_product_data(name: str, brand: str, price: float,
                            member_price: float, quantity: int) -> bool:
        """
        Validates product data fields for correctness and completeness.

        This method ensures all product attributes meet business rules before
        saving to prevent invalid data in the system.

        :param name: Product name (must not be empty).
        :param brand: Product brand (must not be empty).
        :param price: Regular price (must be non-negative).
        :param member_price: Member price (must be non-negative and <= price).
        :param quantity: Stock quantity (must be non-negative).
        :return: True if all validations pass, False otherwise.
        """
        if not name or not brand:
            print("Error: Name and Brand cannot be empty.")
            return False

        if price < 0 or member_price < 0:
            print("Error: Prices cannot be negative.")
            return False

        if member_price > price:
            print("Error: Member price cannot be higher than regular price.")
            return False

        if quantity < 0:
            print("Error: Quantity cannot be negative.")
            return False

        return True


class PromotionManager:
    """
    PromotionManager - Encapsulates product promotion management operations.

    This class centralizes all promotion-related business logic including setting,
    canceling, and listing promotional prices. It demonstrates the Single
    Responsibility Principle by handling only promotion operations.

    """

    @staticmethod
    def set_promotion(products: Dict[str, Any], product_id: str,
                     promo_price: float) -> bool:
        """
        Sets a promotional price for a specific product.

        This method validates that the promotion price is lower than the original
        price before applying it to ensure proper discounting.

        :param products: Dictionary of all product data.
        :param product_id: The unique identifier of the product to promote.
        :param promo_price: The promotional price to set.
        :return: True if promotion was successfully set, False otherwise.
        """
        if product_id not in products:
            print("Product not found.")
            return False

        original_price = products[product_id]['price']
        if promo_price >= original_price:
            print("Promotion price must be less than original price.")
            return False

        products[product_id]['promotion_price'] = promo_price
        print(f"Promotion price set for {products[product_id]['name']}.")
        return True

    @staticmethod
    def cancel_promotion(products: Dict[str, Any], product_id: str) -> bool:
        """
        Cancels an existing promotion for a product.

        This method removes the promotional pricing from a product, reverting
        it to its regular price.

        :param products: Dictionary of all product data.
        :param product_id: The unique identifier of the product.
        :return: True if promotion was successfully cancelled, False otherwise.
        """
        if product_id not in products:
            print("Product not found.")
            return False

        if 'promotion_price' not in products[product_id]:
            print("No promotion set for this product.")
            return False

        del products[product_id]['promotion_price']
        print(f"Promotion cancelled for {products[product_id]['name']}.")
        return True

    @staticmethod
    def list_promotions(products: Dict[str, Any]) -> None:
        """
        Displays all products that currently have active promotions.

        This method filters and presents products with promotional pricing,
        showing both original and promotional prices for comparison.

        :param products: Dictionary of all product data.
        """
        print("\n--- Products with Promotion ---")
        found = False

        for pid, p in products.items():
            if 'promotion_price' in p:
                print(f"ID: {pid} | Name: {p['name']} | "
                      f"Promotion Price: ${p['promotion_price']} | "
                      f"Original Price: ${p['price']}")
                found = True

        if not found:
            print("No products with promotion.")


class PromoCodeAdminManager:
    """
    PromoCodeAdminManager - Manages promotional code CRUD operations for administrators.

    This class provides comprehensive promotional code management including creation,
    editing, deletion, and listing. It handles file-based persistence and validation
    of promo code data, demonstrating the Single Responsibility Principle.

    """

    PROMO_CODE_FILE = 'promo_codes.json'

    @staticmethod
    def load_promo_codes() -> Dict[str, Any]:
        """
        Loads promotional codes from the JSON configuration file.

        If the file doesn't exist, returns a set of default promotional codes
        for common use cases.

        :return: Dictionary mapping promo codes to their configurations.
        """
        if not os.path.exists(PromoCodeAdminManager.PROMO_CODE_FILE):
            # Initialize with default promo codes
            default_codes = {
                'NEWMONASH20': {
                    'discount': 0.20,
                    'description': '20% off for first-time pickup order',
                    'conditions': {
                        'first_time_pickup': True,
                        'pickup_only': True,
                        'min_order': 0
                    }
                },
                'VIP10': {
                    'discount': 0.10,
                    'description': '10% off for VIP members',
                    'conditions': {
                        'vip_only': True,
                        'min_order': 50
                    }
                },
                'MONASH15': {
                    'discount': 0.15,
                    'description': '15% off for Monash students on delivery',
                    'conditions': {
                        'monash_only': True,
                        'delivery_only': True,
                        'min_order': 30
                    }
                }
            }
            PromoCodeAdminManager.save_promo_codes(default_codes)
            return default_codes

        try:
            with open(PromoCodeAdminManager.PROMO_CODE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading promo codes: {e}")
            return {}

    @staticmethod
    def save_promo_codes(promo_codes: Dict[str, Any]) -> bool:
        """
        Saves promotional codes to the JSON configuration file.

        This method persists the current promo code data to ensure changes
        are retained across application sessions.

        :param promo_codes: Dictionary of promo codes to save.
        :return: True if save was successful, False otherwise.
        """
        try:
            with open(PromoCodeAdminManager.PROMO_CODE_FILE, 'w', encoding='utf-8') as f:
                json.dump(promo_codes, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving promo codes: {e}")
            return False

    @staticmethod
    def add_promo_code(code: str, discount: float, description: str,
                      conditions: Dict[str, Any]) -> bool:
        """
        Adds a new promotional code to the system.

        This method validates the promo code data and adds it to the collection
        if all validation checks pass.

        :param code: Promo code string (will be converted to uppercase).
        :param discount: Discount rate as decimal (0.0-1.0, e.g., 0.2 for 20% off).
        :param description: Human-readable description of the promotion.
        :param conditions: Dictionary specifying eligibility requirements.
        :return: True if promo code was successfully added, False otherwise.
        """
        promo_codes = PromoCodeAdminManager.load_promo_codes()
        code = code.upper().strip()

        if code in promo_codes:
            print(f"❌ Promo code '{code}' already exists.")
            return False

        if discount <= 0 or discount > 1:
            print("❌ Discount must be between 0 and 1 (e.g., 0.2 for 20% off).")
            return False

        promo_codes[code] = {
            'discount': discount,
            'description': description,
            'conditions': conditions
        }

        if PromoCodeAdminManager.save_promo_codes(promo_codes):
            print(f"✅ Promo code '{code}' added successfully!")
            return True
        return False

    @staticmethod
    def edit_promo_code(code: str, discount: Optional[float] = None,
                       description: Optional[str] = None,
                       conditions: Optional[Dict[str, Any]] = None) -> bool:
        """
        Edits an existing promotional code's attributes.

        This method allows selective updating of promo code fields. Only
        non-None parameters will be updated, leaving others unchanged.

        :param code: Promo code to edit (case-insensitive).
        :param discount: New discount rate if changing (optional).
        :param description: New description if changing (optional).
        :param conditions: New conditions dictionary if changing (optional).
        :return: True if edit was successful, False otherwise.
        """
        promo_codes = PromoCodeAdminManager.load_promo_codes()
        code = code.upper().strip()

        if code not in promo_codes:
            print(f"❌ Promo code '{code}' not found.")
            return False

        if discount is not None:
            if discount <= 0 or discount > 1:
                print("❌ Discount must be between 0 and 1.")
                return False
            promo_codes[code]['discount'] = discount

        if description is not None:
            promo_codes[code]['description'] = description

        if conditions is not None:
            promo_codes[code]['conditions'] = conditions

        if PromoCodeAdminManager.save_promo_codes(promo_codes):
            print(f"✅ Promo code '{code}' updated successfully!")
            return True
        return False

    @staticmethod
    def delete_promo_code(code: str) -> bool:
        """
        Deletes a promotional code from the system after confirmation.

        This method requires user confirmation before permanently removing
        a promo code to prevent accidental deletions.

        :param code: Promo code to delete (case-insensitive).
        :return: True if successfully deleted, False otherwise.
        """
        promo_codes = PromoCodeAdminManager.load_promo_codes()
        code = code.upper().strip()

        if code not in promo_codes:
            print(f"❌ Promo code '{code}' not found.")
            return False

        confirm = input(f"⚠️  Are you sure you want to delete '{code}'? (y/n): ").lower().strip()
        if confirm == 'y':
            del promo_codes[code]
            if PromoCodeAdminManager.save_promo_codes(promo_codes):
                print(f"✅ Promo code '{code}' deleted successfully!")
                return True
        else:
            print("Deletion cancelled.")
        return False

    @staticmethod
    def list_promo_codes() -> None:
        """
        Displays all promotional codes with their details and conditions.

        This method presents a formatted table showing all promo codes,
        their discount rates, descriptions, and eligibility requirements.
        """
        promo_codes = PromoCodeAdminManager.load_promo_codes()

        if not promo_codes:
            print("\n📋 No promo codes available.")
            return

        print("\n" + "="*80)
        print("  📋 All Promo Codes")
        print("="*80)

        for code, details in promo_codes.items():
            print(f"\n🎟️  Code: {code}")
            print(f"   Discount: {details['discount']*100:.0f}% off")
            print(f"   Description: {details['description']}")
            print(f"   Conditions:")

            conditions = details.get('conditions', {})
            if conditions.get('first_time_pickup'):
                print("     • Only for first-time pickup orders")
            if conditions.get('pickup_only'):
                print("     • Pickup orders only")
            if conditions.get('delivery_only'):
                print("     • Delivery orders only")
            if conditions.get('vip_only'):
                print("     • VIP members only")
            if conditions.get('monash_only'):
                print("     • Monash students only")
            if conditions.get('min_order', 0) > 0:
                print(f"     • Minimum order: ${conditions['min_order']}")

        print("="*80)


class AdminPage(Page):
    """
    AdminPage - Main administrator interface for system management.

    This class provides the administrative interface for managing products,
    promotions, and promotional codes. It demonstrates encapsulation through
    private attributes, inheritance from the Page base class, composition with
    manager classes, and polymorphism through the run() method implementation.

    """

    def __init__(self, products_data: Dict[str, Any], admin_email: str = "admin@monash.edu"):
        """
        Constructs an AdminPage instance with product data and admin email.

        :param products_data: Dictionary mapping product IDs to product information.
        :param admin_email: Email address of the logged-in administrator.
        """
        # Use private attribute for encapsulation
        self.__products = products_data
        self.__admin_email = admin_email
        self.__admin_info = self.__load_admin_info()

    @property
    def products(self) -> Dict[str, Any]:
        """
        Returns the products dictionary for read-only access.

        :return: Dictionary of all products in the system.
        """
        return self.__products

    def run(self) -> None:
        """
        Executes the main administrator menu loop.

        This method implements the abstract run() method from the Page class,
        providing the main interaction loop for administrative functions.
        """
        while True:
            try:
                ScreenManager.clear_screen()
                self.__save_data()
                self.__display_menu()
                choice = InputHandler.get_choice(
                    "Enter your choice: ",
                    valid_choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                    allow_main=True    # Allow returning to main menu
                )

                if not self.__handle_menu_choice(choice):
                    break

            except BackToMainException:
                print("\n↩️  Returning to main menu...")
                input("Press Enter to continue...")
                break
            except ExitApplicationException as e:
                InputHandler.handle_navigation_exception(e)
                break

    def __display_menu(self) -> None:
        """
        Displays the main administrative menu options.

        This private method presents all available administrative functions
        to the user in a formatted menu layout.
        """
        print("\n" + "="*60)
        print("  Welcome Admin in Monash Online Merchant System")
        print("="*60)
        print("1. List All Products")
        print("2. Add a New Product")
        print("3. Edit an Existing Product")
        print("4. Delete a Product")
        print("5. Logout")
        print("6. Search Product by Name")
        print("7. Low Stock Report")
        print("8. Promotion Management")
        print("9. Promo Code Management")
        print("10. View My Profile")
        print("="*60)

    def __handle_menu_choice(self, choice: str) -> bool:
        """
        Processes user menu selection and executes corresponding action.

        This private method centralizes menu routing logic, mapping user
        choices to appropriate handler methods.

        :param choice: User's menu selection as a string.
        :return: False if user wants to logout, True otherwise.
        """
        menu_actions = {
            '1': self.list_products,
            '2': self.add_product,
            '3': self.edit_product,
            '4': self.delete_product,
            '6': self.__search_product,
            '7': self.low_stock_report,
            '8': self.promotion_management,
            '9': self.promo_code_management,
            '10': self.view_profile
        }

        if choice == '5':
            print("Admin logging out...")
            return False
        elif choice in menu_actions:
            menu_actions[choice]()
            return True
        else:
            print("Invalid choice. Please try again.")
            return True

    def __load_admin_info(self) -> Dict[str, Any]:
        """
        Loads administrator information from users data file.

        This private method retrieves the admin's personal information
        including email, name, and contact details.

        :return: Dictionary containing admin information, or default values if not found.
        """
        try:
            # Load users data directly to avoid circular import
            if os.path.exists('users.txt'):
                with open('users.txt', 'r') as f:
                    users_data = json.load(f)
                    if self.__admin_email in users_data:
                        return users_data[self.__admin_email]

            # Return default admin info if not found in users.txt
            return {
                'email': self.__admin_email,
                'first_name': 'Admin',
                'last_name': 'User',
                'mobile_number': 'N/A'
            }
        except Exception as e:
            print(f"Error loading admin information: {e}")
            return {
                'email': self.__admin_email,
                'first_name': 'Admin',
                'last_name': 'User',
                'mobile_number': 'N/A'
            }

    def view_profile(self) -> None:
        """
        Displays the administrator's personal information.

        This method presents the admin's profile including email, full name,
        and mobile number in a formatted layout.
        """
        print("\n" + "="*60)
        print("  👤 Administrator Profile")
        print("="*60)

        print(f"\n📧 Email: {self.__admin_info.get('email', 'N/A')}")
        print(f"👤 First Name: {self.__admin_info.get('first_name', 'N/A')}")
        print(f"👤 Last Name: {self.__admin_info.get('last_name', 'N/A')}")
        print(f"📱 Mobile Number: {self.__admin_info.get('mobile_number', 'N/A')}")

        print("\n" + "="*60)
        input("\nPress Enter to continue...")

    def promotion_management(self) -> None:
        """
        Provides interface for managing product promotional pricing.

        This method displays a submenu for setting, canceling, and listing
        product promotions, delegating operations to PromotionManager.
        """
        print("\n--- Promotion Management ---")
        print("1. Set Promotion Price for a Product")
        print("2. Cancel Promotion for a Product")
        print("3. List Products with Promotion")
        print("4. Back")
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            self.__set_promotion()
        elif choice == '2':
            self.__cancel_promotion()
        elif choice == '3':
            PromotionManager.list_promotions(self.__products)
            input("\nPress Enter to continue...")
        elif choice == '4':
            return
        else:
            print("Invalid choice.")
            input("\nPress Enter to continue...")

    def promo_code_management(self) -> None:
        """
        Provides interface for comprehensive promo code management.

        This method displays a submenu for creating, editing, deleting, and
        listing promotional codes, delegating operations to PromoCodeAdminManager.
        """
        while True:
            print("\n" + "="*60)
            print("  🎟️  Promo Code Management")
            print("="*60)
            print("1. List All Promo Codes")
            print("2. Add New Promo Code")
            print("3. Edit Promo Code")
            print("4. Delete Promo Code")
            print("5. Back to Main Menu")
            print("="*60)

            choice = input("Enter your choice: ").strip()

            if choice == '1':
                PromoCodeAdminManager.list_promo_codes()
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.__add_promo_code()
            elif choice == '3':
                self.__edit_promo_code()
            elif choice == '4':
                self.__delete_promo_code()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

    def __add_promo_code(self) -> None:
        """
        Handles user interaction for adding a new promotional code.

        This private method collects all required promo code information
        from the administrator and validates input before creation.
        """
        print("\n--- Add New Promo Code ---")

        code = input("Enter promo code (e.g., SUMMER25): ").strip().upper()
        if not code:
            print("❌ Promo code cannot be empty.")
            return

        try:
            discount_percent = float(input("Enter discount percentage (e.g., 20 for 20% off): "))
            discount = discount_percent / 100.0
        except ValueError:
            print("❌ Invalid discount percentage.")
            return

        description = input("Enter description: ").strip()
        if not description:
            print("❌ Description cannot be empty.")
            return

        # Collect conditions
        print("\n--- Promo Code Conditions ---")
        conditions = {}

        first_time = input("First-time pickup only? (y/n): ").lower().strip()
        if first_time == 'y':
            conditions['first_time_pickup'] = True

        pickup_only = input("Pickup orders only? (y/n): ").lower().strip()
        if pickup_only == 'y':
            conditions['pickup_only'] = True

        delivery_only = input("Delivery orders only? (y/n): ").lower().strip()
        if delivery_only == 'y':
            conditions['delivery_only'] = True

        vip_only = input("VIP members only? (y/n): ").lower().strip()
        if vip_only == 'y':
            conditions['vip_only'] = True

        monash_only = input("Monash students only? (y/n): ").lower().strip()
        if monash_only == 'y':
            conditions['monash_only'] = True

        try:
            min_order = float(input("Minimum order amount (0 for no minimum): ").strip() or "0")
            if min_order > 0:
                conditions['min_order'] = min_order
        except ValueError:
            print("❌ Invalid minimum order amount. Setting to 0.")
            conditions['min_order'] = 0

        # Add promo code
        PromoCodeAdminManager.add_promo_code(code, discount, description, conditions)
        input("\nPress Enter to continue...")

    def __edit_promo_code(self) -> None:
        """
        Handles user interaction for editing an existing promotional code.

        This private method allows administrators to selectively update
        promo code attributes while preserving unchanged fields.
        """
        print("\n--- Edit Promo Code ---")
        PromoCodeAdminManager.list_promo_codes()

        code = input("\nEnter promo code to edit: ").strip().upper()
        if not code:
            print("❌ Promo code cannot be empty.")
            input("\nPress Enter to continue...")
            return

        promo_codes = PromoCodeAdminManager.load_promo_codes()
        if code not in promo_codes:
            print(f"❌ Promo code '{code}' not found.")
            input("\nPress Enter to continue...")
            return

        print("\nLeave blank to keep current value.")

        # Edit discount
        try:
            discount_input = input(f"New discount percentage (current: {promo_codes[code]['discount']*100:.0f}%): ").strip()
            discount = float(discount_input) / 100.0 if discount_input else None
        except ValueError:
            print("❌ Invalid discount. Keeping current value.")
            discount = None

        # Edit description
        description = input(f"New description (current: {promo_codes[code]['description']}): ").strip()
        description = description if description else None

        # Edit conditions
        edit_conditions = input("Edit conditions? (y/n): ").lower().strip()
        conditions = None

        if edit_conditions == 'y':
            conditions = {}

            first_time = input("First-time pickup only? (y/n): ").lower().strip()
            if first_time == 'y':
                conditions['first_time_pickup'] = True

            pickup_only = input("Pickup orders only? (y/n): ").lower().strip()
            if pickup_only == 'y':
                conditions['pickup_only'] = True

            delivery_only = input("Delivery orders only? (y/n): ").lower().strip()
            if delivery_only == 'y':
                conditions['delivery_only'] = True

            vip_only = input("VIP members only? (y/n): ").lower().strip()
            if vip_only == 'y':
                conditions['vip_only'] = True

            monash_only = input("Monash students only? (y/n): ").lower().strip()
            if monash_only == 'y':
                conditions['monash_only'] = True

            try:
                min_order = float(input("Minimum order amount (0 for no minimum): ").strip() or "0")
                if min_order > 0:
                    conditions['min_order'] = min_order
            except ValueError:
                conditions['min_order'] = 0

        # Update promo code
        PromoCodeAdminManager.edit_promo_code(code, discount, description, conditions)
        input("\nPress Enter to continue...")

    def __delete_promo_code(self) -> None:
        """
        Handles user interaction for deleting a promotional code.

        This private method lists available promo codes and processes
        the administrator's deletion request with confirmation.
        """
        print("\n--- Delete Promo Code ---")
        PromoCodeAdminManager.list_promo_codes()

        code = input("\nEnter promo code to delete: ").strip().upper()
        if code:
            PromoCodeAdminManager.delete_promo_code(code)

        input("\nPress Enter to continue...")

    def __set_promotion(self) -> None:
        """
        Handles user interaction for setting a product promotion.

        This private method collects product ID and promotional price,
        validates the input, and applies the promotion if valid.
        """
        product_id = input("Enter product ID to set promotion: ").strip()

        if product_id not in self.__products:
            print("Product not found.")
            input("\nPress Enter to continue...")
            return

        try:
            product_name = self.__products[product_id]['name']
            promo_price = float(input(f"Enter promotion price for {product_name}: "))

            if PromotionManager.set_promotion(self.__products, product_id, promo_price):
                self.__save_data()
        except ValueError:
            print("Invalid price. Please enter a number.")

        input("\nPress Enter to continue...")

    def __cancel_promotion(self) -> None:
        """
        Handles user interaction for canceling a product promotion.

        This private method collects the product ID and removes its
        promotional pricing if it exists.
        """
        product_id = input("Enter product ID to cancel promotion: ").strip()

        if PromotionManager.cancel_promotion(self.__products, product_id):
            self.__save_data()

        input("\nPress Enter to continue...")

    def list_products(self) -> None:
        """
        Displays all products in the system.

        This method delegates to ProductManager for formatted display
        of all product information.
        """
        ProductManager.display_product_list(self.__products, "All Products")
        input("\nPress Enter to continue...")

    def add_product(self) -> None:
        """
        Handles the process of adding a new product to the system.

        This method collects product information, validates it, and saves
        the new product to the data store.
        """
        print("\n--- Add New Product ---")
        product_id = input("Enter new product ID: ").strip()

        if product_id in self.__products:
            print("Error: Product ID already exists.")
            input("\nPress Enter to continue...")
            return

        # Collect basic product information
        product_data = self.__collect_product_data(product_id)
        if not product_data:
            input("\nPress Enter to continue...")
            return

        # Add to products and save
        self.__products[product_id] = product_data
        self.__save_data()
        print("✅ Product added successfully!")
        input("\nPress Enter to continue...")

    def __collect_product_data(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Collects and validates product data from administrator input.

        This private method prompts for all required product fields,
        validates the input, and handles food-specific attributes.

        :param product_id: The unique identifier for the new product.
        :return: Product data dictionary if valid, None if validation fails.
        """
        name = input("Name: ").strip()
        brand = input("Brand: ").strip()
        description = input("Description: ").strip()
        category = input("Category: ").strip()

        try:
            price = float(input("Price: "))
            member_price = float(input("Member Price: "))
            quantity = int(input("Quantity: "))
        except ValueError:
            print("Error: Price and Quantity must be numbers.")
            return None

        # Validate product data
        if not ProductManager.validate_product_data(name, brand, price, member_price, quantity):
            return None

        product_data = {
            'id': product_id,
            'name': name,
            'brand': brand,
            'description': description,
            'price': price,
            'member_price': member_price,
            'quantity': quantity,
            'category': category
        }

        # Add food-specific fields if category is food
        if category.lower() == 'food':
            product_data.update(self.__collect_food_data())

        return product_data

    def __collect_food_data(self) -> Dict[str, str]:
        """
        Collects food-specific product attributes from user input.

        This private method prompts for expiration date, ingredients,
        storage instructions, and allergen information.

        :return: Dictionary containing food-specific field values.
        """
        return {
            'expiration_date': input("Expiration Date (DD/MM/YYYY): ").strip(),
            'ingredients': input("Ingredients: ").strip(),
            'storage_instructions': input("Storage Instructions: ").strip(),
            'allergens': input("Allergens (comma-separated): ").strip()
        }

    def edit_product(self) -> None:
        """
        Handles the process of editing an existing product.

        This method allows administrators to modify specific product
        attributes while preserving unchanged fields.
        """
        product_id = input("Enter product ID to edit: ").strip()

        if product_id not in self.__products:
            print("Error: Product not found.")
            input("\nPress Enter to continue...")
            return

        product = self.__products[product_id]
        print(f"\n--- Editing Product: {product['name']} ---")

        self.__display_edit_menu()
        edit_choice = input("Enter a number to edit a field (or 'q' to quit): ").strip()

        if self.__handle_edit_choice(product, edit_choice):
            self.__save_data()
            print("✅ Product updated successfully!")
        else:
            print("Product update cancelled or failed.")

        input("\nPress Enter to continue...")

    def __display_edit_menu(self) -> None:
        """
        Displays menu options for editing product fields.

        This private method shows all editable product attributes.
        """
        print("1. Name")
        print("2. Brand")
        print("3. Price")
        print("4. Member Price")
        print("5. Quantity")
        print("6. Description")

    def __handle_edit_choice(self, product: Dict[str, Any], choice: str) -> bool:
        """
        Processes the administrator's product edit selection.

        This private method routes the edit request to the appropriate
        field editor based on user choice.

        :param product: Product dictionary to edit.
        :param choice: User's menu selection.
        :return: True if edit was successful, False otherwise.
        """
        if choice.lower() == 'q':
            return False

        edit_actions = {
            '1': lambda: self.__edit_field(product, 'name', str),
            '2': lambda: self.__edit_field(product, 'brand', str),
            '3': lambda: self.__edit_field(product, 'price', float),
            '4': lambda: self.__edit_field(product, 'member_price', float),
            '5': lambda: self.__edit_field(product, 'quantity', int),
            '6': lambda: self.__edit_field(product, 'description', str)
        }

        if choice in edit_actions:
            return edit_actions[choice]()
        else:
            print("Invalid choice.")
            return False

    def __edit_field(self, product: Dict[str, Any], field: str,
                    field_type: type) -> bool:
        """
        Edits a single product field with type validation.

        This private method handles the input, validation, and updating
        of individual product attributes. Special validation is applied
        for quantity (must be non-negative), prices (must be non-negative),
        and member_price (must not exceed regular price).

        :param product: Product dictionary to modify.
        :param field: Name of the field to edit.
        :param field_type: Expected data type for validation.
        :return: True if edit was successful, False otherwise.
        """
        current_value = product.get(field, 'N/A')
        new_value = input(f"New {field.replace('_', ' ').title()} (current: {current_value}): ").strip()

        try:
            if field_type == str:
                product[field] = new_value
            elif field_type == float:
                float_value = float(new_value)
                # Validate that prices are non-negative
                if field in ['price', 'member_price'] and float_value < 0:
                    print(f"Error: {field.replace('_', ' ').title()} cannot be negative.")
                    return False

                # Validate price relationship: member_price <= price
                if field == 'member_price':
                    if float_value > product.get('price', float('inf')):
                        print(f"Error: Member price (${float_value:.2f}) cannot be higher than regular price (${product.get('price', 0):.2f}).")
                        return False
                elif field == 'price':
                    if float_value < product.get('member_price', 0):
                        print(f"Error: Regular price (${float_value:.2f}) cannot be lower than member price (${product.get('member_price', 0):.2f}).")
                        return False

                product[field] = float_value
            elif field_type == int:
                int_value = int(new_value)
                # Validate that quantity is non-negative (natural number including 0)
                if field == 'quantity' and int_value < 0:
                    print("Error: Quantity cannot be negative. Please enter a natural number (0 or greater).")
                    return False
                product[field] = int_value
            return True
        except ValueError:
            print(f"Invalid input. {field.replace('_', ' ').title()} must be a {field_type.__name__}.")
            return False

    def delete_product(self) -> None:
        """
        Handles product deletion with administrator confirmation.

        This method requires explicit confirmation before permanently
        removing a product from the system.
        """
        product_id = input("Enter product ID to delete: ").strip()

        if product_id not in self.__products:
            print("Error: Product not found.")
            input("\nPress Enter to continue...")
            return

        product_name = self.__products[product_id]['name']
        confirm = input(f"Are you sure you want to delete '{product_name}'? (y/n): ").lower().strip()

        if confirm == 'y':
            del self.__products[product_id]
            self.__save_data()
            print("✅ Product deleted successfully.")
        else:
            print("Deletion cancelled.")

        input("\nPress Enter to continue...")

    def low_stock_report(self) -> None:
        """
        Generates and displays a report of low-stock products.

        This method identifies products below a specified threshold and
        presents them for administrator review.
        """
        threshold = self.__get_stock_threshold()
        low_stock_products = ProductManager.get_low_stock_products(self.__products, threshold)

        if not low_stock_products:
            print(f"No low stock items (<= {threshold}).")
            input("\nPress Enter to continue...")
            return

        ProductManager.display_product_list(
            low_stock_products,
            f"Products with stock <= {threshold}"
        )
        input("\nPress Enter to continue...")

    def __get_stock_threshold(self) -> int:
        """
        Prompts for and validates stock threshold input.

        This private method collects the threshold value from the
        administrator, using a default if no input is provided.

        :return: Stock threshold value as integer.
        """
        try:
            threshold_input = input("Enter stock threshold (default 5): ").strip()
            return int(threshold_input) if threshold_input else ProductManager.LOW_STOCK_DEFAULT_THRESHOLD
        except ValueError:
            print(f"Invalid number. Using default {ProductManager.LOW_STOCK_DEFAULT_THRESHOLD}.")
            return ProductManager.LOW_STOCK_DEFAULT_THRESHOLD

    def __search_product(self) -> None:
        """
        Handles product search by name functionality.

        This private method performs case-insensitive partial matching
        on product names and displays matching results.
        """
        search_term = input("Enter product name to search: ").strip().lower()

        found_products = {
            pid: p for pid, p in self.__products.items()
            if search_term in p['name'].lower()
        }

        if found_products:
            ProductManager.display_product_list(found_products, f"Search Results for '{search_term}'")
        else:
            print(f"No products found matching '{search_term}'.")

        input("\nPress Enter to continue...")

    def __save_data(self) -> None:
        """
        Persists product data to the storage file.

        This private method delegates to DataManager for file-based
        persistence of all product changes.
        """
        from mainPage import DataManager
        DataManager.save_data('products.txt', self.__products)