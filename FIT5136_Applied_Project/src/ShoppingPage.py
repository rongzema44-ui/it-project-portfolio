"""
ShoppingPage - Shopping interface for browsing, filtering, and purchasing products.

This module provides comprehensive shopping functionality including product browsing,
cart management, and checkout processing. It demonstrates OOP principles with clear
separation of concerns and maintainable code structure.

Key Features:
- Product browsing with category and filter support
- Shopping cart management with quantity limits
- Checkout processing with promotion codes
- VIP member discounts and Monash student benefits
- Order creation and inventory management

Author: Applied10_Group6
Version: 3.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from collections import OrderedDict
import json
import os
from InputHandler import InputHandler, BackToMainException, ExitApplicationException


# Abstract base class for all pages
class Page(ABC):
    """
    Page - Abstract base class defining the interface for all page components.

    This class ensures that all page implementations provide a consistent
    interface for navigation and execution using polymorphism.

    Author: Applied10_Group6
    Version: 1.0
    """

    @abstractmethod
    def run(self) -> None:
        """
        Executes the main functionality of the page.

        This method must be implemented by all concrete page classes to define
        their specific behavior and user interaction flow.

        :return: None
        """
        pass


class ScreenManager:
    """"
    ScreenManager - Utility class for managing terminal screen operations.

    This class provides static methods for screen management tasks such as
    clearing the terminal display in a cross-platform manner.

    Author: Applied10_Group6
    Version: 1.0
    """

    @staticmethod
    def clear_screen() -> None:
        """
        Clears the terminal screen in a cross-platform manner.

        This method detects the operating system and uses the appropriate
        command to clear the terminal display.

        :return: None
        """
        os.system('cls' if os.name == 'nt' else 'clear')


class CartDisplay:
    """
    CartDisplay - Handles the display and formatting of shopping cart contents.

    This class encapsulates all cart-related display logic, providing
    clear and consistent formatting for cart items and totals. It demonstrates
    the Single Responsibility Principle by focusing solely on cart display.

    Author: Applied10_Group6
    Version: 1.0
    """

    @staticmethod
    def display_cart(cart: Dict[str, Dict[str, Any]], is_vip: bool) -> float:
        """
        Displays the contents of the shopping cart with formatted output.

        :param cart: Dictionary containing cart items with product information.
        :param is_vip: Boolean indicating if the user has VIP status.
        :return: The total amount of all items in the cart.
        """
        if not cart:
            print("\n🛒 Your cart is empty.")
            return 0.0

        print("\n" + "="*60)
        print("🛒 YOUR SHOPPING CART")
        print("="*60)

        total_amount = 0.0
        total_items = 0

        for product_id, item_info in cart.items():
            product = item_info['product']
            quantity = item_info['quantity']
            price = CartDisplay._get_product_price(product, is_vip)
            subtotal = price * quantity

            regular_price = product['price']
            member_price = product.get('member_price', regular_price)

            print(f"📦 {product['name']}")
            print(f"   Regular Price: ${regular_price:.2f} | Member Price: ${member_price:.2f}")
            print(f"   Quantity: {quantity} | Unit Price: ${price:.2f} | Subtotal: ${subtotal:.2f}")

            if is_vip and 'member_price' in product:
                savings = (regular_price - member_price) * quantity
                print(f"   💎 VIP Discount Applied! You save: ${savings:.2f}")
            print()

            total_amount += subtotal
            total_items += quantity

        print("-" * 60)
        print(f"Total Items: {total_items}")
        print(f"Total Amount: ${total_amount:.2f}")

        if is_vip:
            print("💎 VIP Member Discounts Applied!")

        print("=" * 60)
        return total_amount

    @staticmethod
    def _get_product_price(product: Dict[str, Any], is_vip: bool) -> float:
        """
        Retrieves the appropriate price for a product based on VIP status.

        :param product: Dictionary containing product information.
        :param is_vip: Boolean indicating if the user has VIP status.
        :return: The price to use for the product.
        """
        if is_vip and 'member_price' in product:
            return product['member_price']
        return product['price']

    @staticmethod
    def display_products(products_list: List[Dict[str, Any]]) -> None:
        """
        Displays a formatted list of products in a table format.

        Products are sorted to show in-stock items first, followed by out-of-stock items.
        This ensures better user experience by prioritizing available products.

        :param products_list: List of product dictionaries to display.
        """
        if not products_list:
            print("No products to display.")
            return

        # Separate in-stock and out-of-stock products
        in_stock_products = [p for p in products_list if p.get('quantity', 0) > 0]
        out_of_stock_products = [p for p in products_list if p.get('quantity', 0) == 0]

        # Combine: in-stock first, then out-of-stock
        sorted_products = in_stock_products + out_of_stock_products

        print(f"{'ID':<8} {'Name':<25} {'Price':<12} {'Member Price':<12} {'Quantity':<10}")
        print("-" * 75)

        for p in sorted_products:
            member_price = p.get('member_price', p['price'])
            quantity_display = p['quantity'] if p['quantity'] > 0 else "OUT OF STOCK"
            print(f"{p['id']:<8} {p['name']:<25} ${p['price']:<11.2f} ${member_price:<11.2f} {quantity_display}")

        print(f"Total products: {len(products_list)}")


class PromoCodeManager:
    """
    PromoCodeManager - Manages promotion codes including validation and application.

    This class handles all promotion code operations including loading codes
    from storage, validating conditions, and calculating discounts. It provides
    centralized promotion code management with support for various discount types.

    Author: Applied10_Group6
    Version: 1.0
    """

    PROMO_CODE_FILE = 'promo_codes.json'

    @staticmethod
    def load_promo_codes() -> Dict[str, Any]:
        """
        Loads promotion codes from the JSON configuration file.

        If the file doesn't exist, returns a set of default promotion codes
        for common use cases.

        :return: Dictionary of promotion codes and their configurations.
        """
        if not os.path.exists(PromoCodeManager.PROMO_CODE_FILE):
            # Return default promo codes if file doesn't exist
            return {
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

        try:
            with open(PromoCodeManager.PROMO_CODE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading promo codes: {e}")
            return {}

    @staticmethod
    def validate_promo_code(promo_code: str, is_pickup: bool, is_first_pickup: bool,
                           is_vip: bool = False, is_monash: bool = False,
                           total_amount: float = 0) -> Optional[float]:
        """
        Validates a promotion code against all applicable conditions.

        :param promo_code: The promotion code to validate.
        :param is_pickup: Whether the order is for pickup.
        :param is_first_pickup: Whether this is the user's first pickup order.
        :param is_vip: Whether the user has VIP status.
        :param is_monash: Whether the user is a Monash student.
        :param total_amount: The total order amount before discounts.
        :return: Discount rate if valid, None if invalid.
        """
        promo_code = promo_code.upper().strip()
        promo_codes = PromoCodeManager.load_promo_codes()

        if promo_code not in promo_codes:
            return None

        promo = promo_codes[promo_code]
        conditions = promo.get('conditions', {})

        # Check first-time pickup requirement
        if conditions.get('first_time_pickup') and not is_first_pickup:
            print(f"❌ {promo_code} is only valid for first-time pickup orders.")
            return None

        # Check pickup-only requirement
        if conditions.get('pickup_only') and not is_pickup:
            print(f"❌ {promo_code} is only valid for pickup orders.")
            return None

        # Check delivery-only requirement
        if conditions.get('delivery_only') and is_pickup:
            print(f"❌ {promo_code} is only valid for delivery orders.")
            return None

        # Check VIP-only requirement
        if conditions.get('vip_only') and not is_vip:
            print(f"❌ {promo_code} is only valid for VIP members.")
            return None

        # Check Monash-only requirement
        if conditions.get('monash_only') and not is_monash:
            print(f"❌ {promo_code} is only valid for Monash students.")
            return None

        # Check minimum order amount
        min_order = conditions.get('min_order', 0)
        if total_amount < min_order:
            print(f"❌ {promo_code} requires minimum order of ${min_order:.2f}")
            return None

        # All conditions met
        discount = promo['discount']
        print(f"✅ Promo code '{promo_code}' applied: {promo['description']}")
        return discount

    @staticmethod
    def list_available_promos() -> None:
        """
        Display all available promo codes with their conditions.

        :return: None
        """
        promo_codes = PromoCodeManager.load_promo_codes()

        if not promo_codes:
            print("\n🎁 No promo codes available at the moment.")
            return

        print("\n🎁 Available Promo Codes:")
        print("="*60)
        for code, promo in promo_codes.items():
            print(f"Code: {code}")
            print(f"  Discount: {int(promo['discount']*100)}% off")
            print(f"  {promo['description']}")
            conditions = promo.get('conditions', {})
            if conditions:
                print("  Conditions:")
                if conditions.get('first_time_pickup'):
                    print("    - First-time pickup only")
                if conditions.get('pickup_only'):
                    print("    - Pickup orders only")
                if conditions.get('delivery_only'):
                    print("    - Delivery orders only")
                if conditions.get('vip_only'):
                    print("    - VIP members only")
                if conditions.get('monash_only'):
                    print("    - Monash students only")
                if conditions.get('min_order', 0) > 0:
                    print(f"    - Minimum order: ${conditions['min_order']:.2f}")
            print()
        print("="*60)


class CheckoutProcessor:
    """
    CheckoutProcessor - Encapsulates checkout processing logic.

    This class provides centralized checkout operations including cart total
    calculation, stock validation, and inventory updates. It demonstrates
    the Single Responsibility Principle by focusing solely on checkout-related
    operations.

    Author: Applied10_Group6
    Version: 1.0
    """

    @staticmethod
    def calculate_total(cart: Dict[str, Dict[str, Any]], is_vip: bool) -> float:
        """
        Calculate total amount for cart items.

        :param cart: Dictionary containing cart items with product information.
        :param is_vip: Boolean indicating if the user has VIP status.
        :return: Total amount as float.
        """
        total = 0.0
        for item_info in cart.values():
            product = item_info['product']
            quantity = item_info['quantity']
            price = CartDisplay._get_product_price(product, is_vip)
            total += price * quantity
        return total

    @staticmethod
    def validate_stock(cart: Dict[str, Dict[str, Any]]) -> bool:
        """
        Validate that all products in cart have sufficient stock.

        :param cart: Dictionary containing cart items with product information.
        :return: True if all products available, False otherwise.
        """
        for product_id, item_info in cart.items():
            product = item_info['product']
            quantity = item_info['quantity']

            if product['quantity'] < quantity:
                print(f"\n❌ Insufficient stock for {product['name']}. Available: {product['quantity']}")
                input("Press Enter to continue...")
                return False

        return True

    @staticmethod
    def update_stock(cart: Dict[str, Dict[str, Any]]) -> None:
        """
        Update product quantities after purchase.

        :param cart: Dictionary containing cart items with product information.
        :return: None
        """
        for item_info in cart.values():
            product = item_info['product']
            quantity = item_info['quantity']
            product['quantity'] -= quantity


class Shopping(Page):
    """
    Shopping - Main shopping interface for product browsing and purchase management.

    This class implements the Page interface and provides comprehensive
    shopping functionality including product discovery, cart management,
    and checkout processing. It demonstrates OOP principles including
    encapsulation, composition, and polymorphism.

    Author: Applied10_Group6
    Version: 3.0
    """
    def view_cart(self) -> None:
        """
        Display shopping cart with formatted output.

        Demonstrates composition by delegating display logic to CartDisplay class.

        :return: None
        """
        CartDisplay.display_cart(self.__cart, self.__is_vip)
        #input("\nPress Enter to continue...")

    def display_products(self, products_list: List[Dict[str, Any]]) -> None:
        """
        Display list of products in formatted table.

        Demonstrates composition by delegating display logic to CartDisplay class.

        :param products_list: List of product dictionaries to display.
        :return: None
        """
        CartDisplay.display_products(products_list)

    def search_products(self) -> None:
        """
        Search for products by keyword in name or description.

        This method prompts the user for a search term and displays matching
        products. Demonstrates encapsulation by keeping search logic internal.

        :return: None
        """
        search_term = input("\n🔍 Enter product name or keyword to search: ").strip().lower()

        if not search_term:
            print("❌ Please enter a search term.")
            return

        found_products = [
            p for p in self.__products.values()
            if search_term in p['name'].lower() or search_term in p.get('description', '').lower()
        ]

        if not found_products:
            print(f"❌ No products found for '{search_term}'.")
            input("\nPress Enter to continue...")
            return

        print(f"\n🔍 Search results for '{search_term}':")
        self.display_products(found_products)
        input("\nPress Enter to continue...")

    def view_all_products(self) -> None:
        """
        Display all available products in the system.

        :return: None
        """
        print("\n📋 ALL AVAILABLE PRODUCTS")
        print("-" * 60)
        self.display_products(list(self.products.values()))
        input("\nPress Enter to continue...")

    def add_to_cart(self):
        """
        Add a product to the shopping cart with quantity validation.

        This method prompts for product ID and quantity, validates stock
        availability and cart limits, then adds the item to the cart.

        :return: None
        """
        product_id = input("Enter product ID to add to cart: ").strip()
        if product_id not in self.products:
            print("❌ Invalid product ID. Please check the product list.")
            input("\nPress Enter to continue...")
            return
        product = self.products[product_id]
        if product['quantity'] == 0:
            print(f"❌ Sorry, '{product['name']}' is currently out of stock.")
            input("\nPress Enter to continue...")
            return
        try:
            quantity = int(input(f"Enter quantity (1-10, available: {product['quantity']}): ").strip())
        except ValueError:
            print("❌ Quantity must be a number.")
            input("\nPress Enter to continue...")
            return
        if quantity <= 0:
            print("❌ Quantity must be at least 1.")
            input("\nPress Enter to continue...")
            return
        if quantity > 10:
            print("❌ Cannot add more than 10 of a single product.")
            input("\nPress Enter to continue...")
            return
        if product['quantity'] < quantity:
            print(f"❌ Only {product['quantity']} available in stock.")
            input("\nPress Enter to continue...")
            return
        if len(self.cart) >= 20:
            print("❌ Cannot add more items. Cart limit of 20 items reached.")
            input("\nPress Enter to continue...")
            return
        # Add to cart
        if product_id in self.cart:
            new_quantity = self.cart[product_id]['quantity'] + quantity
            if new_quantity > 10:
                print(f"❌ Cannot exceed 10 items total for this product. You already have {self.cart[product_id]['quantity']} in cart.")
                input("\nPress Enter to continue...")
                return
            self.cart[product_id]['quantity'] = new_quantity
        else:
            self.cart[product_id] = {'product': product, 'quantity': quantity}
        print(f"✅ Added {quantity} of '{product['name']}' to cart.")
        input("\nPress Enter to continue...")  # Wait for user to read success message

    def get_cart(self):
        """
        Retrieves the current shopping cart.

        :return: The shopping cart dictionary.
        """
        return self.cart

    def browse_by_category(self):
        """
        Displays products organized by category for user browsing.

        This method shows all available product categories and allows users
        to select a category to view its products.
        """
        categories = sorted(set(p['category'] for p in self.products.values()))
        print("\n📂 AVAILABLE CATEGORIES:")
        print("-" * 30)
        for i, category in enumerate(categories, 1):
            product_count = sum(1 for p in self.products.values() if p['category'] == category)
            print(f"{i}. {category} ({product_count} products)")
        try:
            choice = input("\nEnter category name or number: ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(categories):
                    category = categories[choice_num - 1]
                else:
                    print("❌ Invalid category number.")
                    return
            else:
                category = choice
            found_products = [p for p in self.products.values() if p['category'].lower() == category.lower()]
            if not found_products:
                print(f"❌ No products found in category '{category}'.")
                input("\nPress Enter to continue...")
                return
            print(f"\n📦 Products in '{category}':")
            self.display_products(found_products)
            input("\nPress Enter to continue...")
        except (ValueError, IndexError):
            print("❌ Invalid input. Please try again.")
            input("\nPress Enter to continue...")
    def browse(self):
        """
        Provides the main product browsing interface.

        This method displays the browsing menu and handles user navigation
        between different shopping functionalities. It serves as the primary
        entry point for product browsing from UserPage, supporting navigation
        commands for returning to main menu or exiting.

        :return: None
        :raises BackToMainException: If user requests return to main menu.
        :raises ExitApplicationException: If user requests application exit.
        """
        while True:
            try:
                ScreenManager.clear_screen()
                print("\n" + "="*50)
                print("🛍️  PRODUCT BROWSING")
                print("="*50)
                print("1. Browse by Category")
                print("2. Filter Products")
                print("3. Search Products")
                print("4. View All Products")
                print("5. Add to Cart")
                print("6. View Available Promo Codes")
                print("7. Back to Main Menu")
                print("-"*50)

                choice = InputHandler.get_choice(
                    "Enter your choice (1-7): ",
                    valid_choices=['1', '2', '3', '4', '5', '6', '7'],
                    allow_main=True    # Allow returning to main menu
                )

                if choice == '1':
                    self.browse_by_category()
                elif choice == '2':
                    self.filter_products()
                elif choice == '3':
                    self.search_products()
                elif choice == '4':
                    self.view_all_products()
                elif choice == '5':
                    self.add_to_cart()
                elif choice == '6':
                    self.show_available_promos()
                elif choice == '7':
                    print("Returning to main menu...")
                    break

            except BackToMainException:
                print("\n↩️  Returning to main menu...")
                input("Press Enter to continue...")
                break
            except ExitApplicationException:
                # Let this propagate up to the main loop
                raise

    def __init__(self, products: Dict[str, Any], user_email: str,
                 users: Dict[str, Any], cart: Dict[str, Dict[str, Any]]):
        """
        Constructs a Shopping instance with the specified data.

        :param products: Dictionary of all available products.
        :param user_email: Email address of the current user.
        :param users: Dictionary of all system users.
        :param cart: User's shopping cart contents.
        """
        # Use private attributes for encapsulation
        self.__products = products
        self.__user_email = user_email
        self.__users = users
        # Ensure cart is OrderedDict to maintain insertion order (requirement 2.4)
        if not isinstance(cart, OrderedDict):
            self.__cart = OrderedDict(cart)
        else:
            self.__cart = cart
        self.__is_vip = self.__users[self.__user_email].get('is_vip', False)

    # Property decorators for controlled access (Encapsulation)
    @property
    def products(self) -> Dict[str, Any]:
        """
        Retrieves the products dictionary.

        :return: Dictionary containing all product data.
        """
        return self.__products

    @property
    def user_email(self) -> str:
        """
        Get current user's email address.

        :return: User's email as string.
        """
        return self.__user_email

    @property
    def users(self) -> Dict[str, Any]:
        """
        Get users dictionary.

        :return: Dictionary containing all user data.
        """
        return self.__users

    @property
    def cart(self) -> Dict[str, Dict[str, Any]]:
        """
        Get shopping cart.

        :return: Dictionary containing cart items.
        """
        return self.__cart

    @property
    def is_vip(self) -> bool:
        """
        Get VIP status of current user.

        :return: True if user has VIP status, False otherwise.
        """
        return self.__is_vip

    def run(self) -> None:
        """
        Run the shopping page main loop.

        Polymorphism: Implements abstract run() method from Page class.

        :return: None
        """
        self.browse()

    def get_cart(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the cart dictionary.

        :return: Shopping cart dictionary.
        """
        return self.__cart

    def get_users(self) -> Dict[str, Any]:
        """
        Get the users dictionary.

        :return: Users data dictionary.
        """
        return self.__users

    def get_products(self) -> Dict[str, Any]:
        """
        Get the products dictionary.

        :return: Products data dictionary.
        """
        return self.__products

    def get_monash_status(self) -> bool:
        """
        Check if user is a Monash student.

        :return: True if Monash student, False otherwise.
        """
        return self.__users[self.__user_email].get('is_monash_student', False)

    def get_profile_address(self) -> str:
        """
        Get user's delivery address from profile.

        :return: User's address as string.
        """
        return self.__users[self.__user_email].get('address', '')

    def get_customer_name(self) -> str:
        """
        Get user's name or email as fallback.

        :return: User's name or email as string.
        """
        return self.__users[self.__user_email].get('name', self.__user_email)

    def get_funds(self) -> float:
        """
        Get user's available account balance.

        :return: User's balance as float.
        """
        return self.__users[self.__user_email].get('balance', 1000)

    def deduct_funds(self, amount: float) -> None:
        """
        Deduct amount from user's account balance.

        :param amount: Amount to deduct.
        :return: None
        """
        self.__users[self.__user_email]['balance'] -= amount

    def update_inventory(self) -> None:
        """
        Update product inventory after purchase completion.

        :return: None
        """
        CheckoutProcessor.update_stock(self.__cart)

    def is_first_time_pickup(self) -> bool:
        """
        Check if this is user's first-time pickup order.

        :return: True if first-time pickup, False otherwise.
        """
        user = self.__users[self.__user_email]
        return not user.get('has_pickup_order', False)

    def set_pickup_flag(self) -> None:
        """
        Marks that the user has completed a pickup order.

        :return: None
        """
        self.__users[self.__user_email]['has_pickup_order'] = True

    def apply_promo_code(self, promo_code: str, is_pickup: bool,
                        is_first_pickup: bool, total_amount: float = 0) -> float:
        """
        Applies and validates a promotion code.

        :param promo_code: The promotion code to apply.
        :param is_pickup: Whether the order is for pickup.
        :param is_first_pickup: Whether this is the first pickup order.
        :param total_amount: Total order amount before discount.
        :return: Discount rate if valid, 0.0 if invalid.
        """
        discount = PromoCodeManager.validate_promo_code(
            promo_code=promo_code,
            is_pickup=is_pickup,
            is_first_pickup=is_first_pickup,
            is_vip=self.__is_vip,
            is_monash=self.get_monash_status(),
            total_amount=total_amount
        )
        return discount if discount is not None else 0.0

    def get_pickup_stores(self) -> List[Dict[str, str]]:
        """
        Retrieves the list of available pickup stores.

        :return: List of dictionaries containing store information.
        """
        return [
            {
                'name': 'Monash Caulfield Campus Store',
                'address': '900 Dandenong Rd, Caulfield East VIC 3145',
                'phone': '(03) 9903 1234',
                'hours': 'Mon-Fri 8am-8pm, Sat-Sun 9am-6pm'
            },
            {
                'name': 'Monash Clayton Campus Store',
                'address': 'Wellington Rd, Clayton VIC 3800',
                'phone': '(03) 9905 5678',
                'hours': 'Mon-Fri 7am-9pm, Sat-Sun 9am-7pm'
            },
            {
                'name': 'Melbourne CBD Store',
                'address': '123 Collins St, Melbourne VIC 3000',
                'phone': '(03) 9600 9999',
                'hours': 'Mon-Sun 9am-9pm'
            }
        ]

    def show_available_promos(self) -> None:
        """
        Displays available promotion codes to the user.

        :return: None
        """
        PromoCodeManager.list_available_promos()
        input("\nPress Enter to continue...")

    def filter_products(self):
        """
        Displays the product filtering menu and handles user selection.

        This method provides various filtering options to help users
        narrow down product selections based on different criteria.
        """
        print("\n FILTER PRODUCTS")
        print("-" * 30)
        print("Filtering options:")
        print("1. By Price Range")
        print("2. By Brand")
        print("3. By Availability")
        print("4. By Category")
        print("5. By Subcategory")
        print("6. Back to Browsing")
        choice = input("Enter your choice (1-6): ").strip()
        if choice == '1':
            self.filter_by_price()
        elif choice == '2':
            self.filter_by_brand()
        elif choice == '3':
            self.filter_by_availability()
        elif choice == '4':
            self.filter_by_category()
        elif choice == '5':
            self.filter_by_subcategory()
        elif choice == '6':
            return
        else:
            print("❌ Invalid choice.")

    def filter_by_price(self) -> None:
        """
        Filters products based on a specified price range.

        This method prompts the user for minimum and maximum price values,
        validates the input, and displays products within the specified range.

        :raises ValueError: If non-numeric input is provided for prices.
        """
        try:
            min_price = float(input("Enter minimum price: $").strip())
            max_price = float(input("Enter maximum price: $").strip())

            if min_price < 0 or max_price < 0:
                print("❌ Prices cannot be negative.")
                return

            if min_price > max_price:
                print("❌ Minimum price cannot be greater than maximum price.")
                return

            filtered = [
                p for p in self.__products.values()
                if min_price <= p['price'] <= max_price
            ]

            if not filtered:
                print(f"❌ No products found in price range ${min_price:.2f} - ${max_price:.2f}")
                input("\nPress Enter to continue...")
                return

            print(f"\n💰 Products in price range ${min_price:.2f} - ${max_price:.2f}:")
            self.display_products(filtered)
            input("\nPress Enter to continue...")

        except ValueError:
            print("❌ Invalid price. Please enter numbers only.")
            input("\nPress Enter to continue...")

    def filter_by_brand(self) -> None:
        """
        Filters products by brand name.

        This method displays all available brands and allows the user
        to select a brand to view its associated products.
        """
        # Get unique brands
        brands = set(p['brand'] for p in self.__products.values() if 'brand' in p)

        if not brands:
            print("❌ No brands available.")
            return

        print("\n🏷️ Available brands:")
        for i, brand in enumerate(sorted(brands), 1):
            print(f"{i}. {brand}")

        brand_name = input("\nEnter brand name to filter: ").strip()

        filtered = [
            p for p in self.__products.values()
            if p.get('brand', '').lower() == brand_name.lower()
        ]

        if not filtered:
            print(f"❌ No products found for brand '{brand_name}'")
            input("\nPress Enter to continue...")
            return

        print(f"\n🏷️ Products from brand '{brand_name}':")
        self.display_products(filtered)
        input("\nPress Enter to continue...")

    def filter_by_availability(self) -> None:
        """
        Filters products based on stock availability.

        This method provides options to filter products by their current
        stock status: in stock, out of stock, or low stock (5 or fewer items).
        """
        print("\n📦 Filter by availability:")
        print("1. In Stock")
        print("2. Out of Stock")
        print("3. Low Stock (≤5)")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == '1':
            filtered = [p for p in self.__products.values() if p.get('quantity', 0) > 0]
            title = "In Stock Products"
        elif choice == '2':
            filtered = [p for p in self.__products.values() if p.get('quantity', 0) == 0]
            title = "Out of Stock Products"
        elif choice == '3':
            filtered = [p for p in self.__products.values() if 0 < p.get('quantity', 0) <= 5]
            title = "Low Stock Products (≤5)"
        else:
            print("❌ Invalid choice.")
            input("\nPress Enter to continue...")
            return

        if not filtered:
            print(f"❌ No products found for selected filter.")
            input("\nPress Enter to continue...")
            return

        print(f"\n📦 {title}:")
        self.display_products(filtered)
        input("\nPress Enter to continue...")

    def filter_by_category(self) -> None:
        """
        Filters products by category.

        This method displays all available product categories and allows
        the user to select a category to view its associated products.
        """
        # Get all unique categories
        categories = {}
        for product in self.__products.values():
            category = product.get('category', 'Unknown')
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        if not categories:
            print("❌ No categories found.")
            input("\nPress Enter to continue...")
            return

        # Display categories
        print("\n📂 Available Categories:")
        category_list = sorted(categories.items())
        for idx, (cat, count) in enumerate(category_list, 1):
            print(f"{idx}. {cat} ({count} products)")

        # Get user choice
        try:
            choice = input("\nEnter category number or name: ").strip()

            # Try to parse as number first
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(category_list):
                    selected_category = category_list[choice_idx][0]
                else:
                    print("❌ Invalid category number.")
                    input("\nPress Enter to continue...")
                    return
            else:
                # Try to match by name
                selected_category = None
                for cat, _ in category_list:
                    if cat.lower() == choice.lower():
                        selected_category = cat
                        break

                if not selected_category:
                    print(f"❌ Category '{choice}' not found.")
                    input("\nPress Enter to continue...")
                    return

            # Filter products by selected category
            filtered = [p for p in self.__products.values()
                       if p.get('category', '').lower() == selected_category.lower()]

            if not filtered:
                print(f"❌ No products found in category '{selected_category}'")
                input("\nPress Enter to continue...")
                return

            print(f"\n📂 Products in category '{selected_category}':")
            self.display_products(filtered)
            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"❌ Error filtering by category: {e}")
            input("\nPress Enter to continue...")

    def filter_by_subcategory(self) -> None:
        """
        Filter products by subcategory with category grouping.

        This method displays subcategories grouped by their parent categories
        and allows users to select a subcategory to view its products.
        Demonstrates encapsulation by keeping filtering logic internal.

        :return: None
        """
        # Get all unique subcategories grouped by category
        categories = {}
        for product in self.__products.values():
            category = product.get('category', 'Unknown')
            subcategory = product.get('subcategory', 'Unknown')

            if category not in categories:
                categories[category] = {}

            if subcategory not in categories[category]:
                categories[category][subcategory] = 0
            categories[category][subcategory] += 1

        if not categories:
            print("❌ No subcategories found.")
            input("\nPress Enter to continue...")
            return

        # Display subcategories grouped by category
        print("\n📂 Available Subcategories:")
        subcategory_list = []
        idx = 1
        for category in sorted(categories.keys()):
            print(f"\n{category}:")
            for subcategory, count in sorted(categories[category].items()):
                print(f"  {idx}. {subcategory} ({count} products)")
                subcategory_list.append((category, subcategory))
                idx += 1

        # Get user choice
        try:
            choice = input("\nEnter subcategory number or name: ").strip()

            # Try to parse as number first
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(subcategory_list):
                    selected_category, selected_subcategory = subcategory_list[choice_idx]
                else:
                    print("❌ Invalid subcategory number.")
                    input("\nPress Enter to continue...")
                    return
            else:
                # Try to match by name
                selected_subcategory = None
                for cat, subcat in subcategory_list:
                    if subcat.lower() == choice.lower():
                        selected_category = cat
                        selected_subcategory = subcat
                        break

                if not selected_subcategory:
                    print(f"❌ Subcategory '{choice}' not found.")
                    input("\nPress Enter to continue...")
                    return

            # Filter products by selected subcategory
            filtered = [p for p in self.__products.values()
                       if p.get('subcategory', '').lower() == selected_subcategory.lower()]

            if not filtered:
                print(f"❌ No products found in subcategory '{selected_subcategory}'")
                input("\nPress Enter to continue...")
                return

            print(f"\n📂 Products in subcategory '{selected_subcategory}' ({selected_category}):")
            self.display_products(filtered)
            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"❌ Error filtering by subcategory: {e}")
            input("\nPress Enter to continue...")

    def cart_actions(self):
        """
        Displays the cart management menu and handles user interactions.

        This method provides various cart operations including editing quantities,
        removing items, emptying the cart, and proceeding to checkout.
        """
        while True:
            print("\n🛒 CART ACTIONS")
            print("-" * 30)
            print("1. Edit item quantity")
            print("2. Remove item")
            print("3. Empty cart")
            print("4. Continue shopping")
            print("5. Checkout")
            print("6. Back to main menu")

            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                self.edit_cart_item()
            elif choice == '2':
                self.remove_cart_item()
            elif choice == '3':
                self.empty_cart()
                break
            elif choice == '4':
                print("Continuing shopping...")
                break
            elif choice == '5':
                self.checkout()
                break
            elif choice == '6':
                print("Returning to main menu...")
                break
            else:
                print("❌ Invalid choice. Please try again.")

    def edit_cart_item(self):
        """
        Allows the user to modify the quantity of an item in the shopping cart.

        This method prompts the user for a product ID and new quantity,
        validates the input, and updates the cart accordingly.
        """
        if not self.cart:
            print("❌ Your cart is empty.")
            input("\nPress Enter to continue...")
            return

        product_id = input("Enter product ID to edit: ").strip()

        if product_id not in self.cart:
            print("❌ Product not found in cart.")
            input("\nPress Enter to continue...")
            return

        product = self.cart[product_id]['product']
        current_quantity = self.cart[product_id]['quantity']

        print(f"Current quantity of '{product['name']}': {current_quantity}")
        print(f"Available in stock: {product['quantity']}")

        try:
            new_quantity = int(input("Enter new quantity (0 to remove): ").strip())
        except ValueError:
            print("❌ Quantity must be a number.")
            input("\nPress Enter to continue...")
            return

        if new_quantity == 0:
            del self.cart[product_id]
            print("✅ Item removed from cart.")
            input("\nPress Enter to continue...")
            return

        if new_quantity < 0:
            print("❌ Quantity cannot be negative.")
            input("\nPress Enter to continue...")
            return

        if new_quantity > 10:
            print("❌ Cannot have more than 10 of a single product.")
            input("\nPress Enter to continue...")
            return

        if product['quantity'] < new_quantity:
            print(f"❌ Only {product['quantity']} available in stock.")
            input("\nPress Enter to continue...")
            return

        self.cart[product_id]['quantity'] = new_quantity
        print(f"✅ Quantity updated to {new_quantity}.")
        input("\nPress Enter to continue...")

    def remove_cart_item(self):
        """
        Removes a specific item from the shopping cart.

        This method prompts the user for a product ID and removes
        the corresponding item from the cart if it exists.
        """
        if not self.cart:
            print("❌ Your cart is empty.")
            input("\nPress Enter to continue...")
            return

        product_id = input("Enter product ID to remove: ").strip()

        if product_id in self.cart:
            product_name = self.cart[product_id]['product']['name']
            del self.cart[product_id]
            print(f"✅ '{product_name}' removed from cart.")
            input("\nPress Enter to continue...")
        else:
            print("❌ Product not found in cart.")
            input("\nPress Enter to continue...")

    def empty_cart(self):
        """
        Empties the entire shopping cart after user confirmation.

        This method prompts the user for confirmation before clearing
        all items from the shopping cart.
        """
        if not self.cart:
            print("❌ Your cart is already empty.")
            input("\nPress Enter to continue...")
            return

        confirm = input("⚠️  Are you sure you want to empty the entire cart? (y/n): ").lower().strip()
        if confirm == 'y':
            self.cart.clear()
            print("✅ Cart emptied.")
            input("\nPress Enter to continue...")
        else:
            print("Cart clearing cancelled.")
            input("\nPress Enter to continue...")

    def checkout(self):
        """
        Processes the checkout procedure for items in the shopping cart.

        This method handles the complete checkout process including:
        - Delivery option selection
        - Address/store selection
        - Price calculation
        - Promotion code application
        - Payment processing
        - Order confirmation

        :raises Exception: If any error occurs during the checkout process.
        """
        if not self.cart:
            print("\n❌ Your cart is empty. Fail to checkout.")
            input("Press Enter to continue...")
            return

        print("\n" + "="*50)
        print(" CHECKOUT")
        print("="*50)

        is_monash = self.get_monash_status()
        is_vip = self.is_vip
        customer_name = self.get_customer_name()
        email = self.user_email

        # 1. Delivery or pickup option selection
        print("\n" + "="*60)
        print(" DELIVERY OPTIONS")
        print("="*60)

        if is_monash:
            print("🎓 Monash Student Benefits:")
            print("   • Delivery: FREE (Regular: AUD $20)")
            print("   • Pickup: 5% discount (Cannot combine with promo codes)")
            print()

        print("1. Delivery{}".format(" - FREE for Monash students ✨" if is_monash else " (AUD $20 fee)"))
        print("2. Pickup{}".format(" - 5% Monash student discount ✨" if is_monash else " (No delivery fee)"))

        while True:
            delivery_choice = input("\nEnter 1 for Delivery, 2 for Pickup: ").strip()
            if delivery_choice in ('1', '2'):
                break
            print("❌ Invalid choice. Please enter 1 or 2.")
        is_pickup = delivery_choice == '2'

        delivery_fee = 0
        pickup_discount = 0
        promo_discount = 0
        promo_code_used = ''

        # 2. Address or store selection
        if is_pickup:
            stores = self.get_pickup_stores()
            print("\nAvailable Pickup Stores:")
            for idx, s in enumerate(stores, 1):
                print(f"{idx}. {s['name']} | {s['address']} | {s['phone']} | Hours: {s['hours']}")
            while True:
                store_choice = input("Select pickup store (number): ").strip()
                if store_choice.isdigit() and 1 <= int(store_choice) <= len(stores):
                    pickup_store = stores[int(store_choice)-1]
                    break
                print("Invalid store selection.")
        else:
            print("\nDelivery address:")
            default_addr = self.get_profile_address()
            print(f"Default: {default_addr}")
            use_default = input("Use default address? (y/n): ").strip().lower() == 'y'
            if use_default:
                delivery_address = default_addr
            else:
                delivery_address = input("Enter delivery address (not saved): ").strip()

        # 3. Calculate total price
        item_list = []
        total_price = 0
        for product_id, item_info in self.cart.items():
            product = item_info['product']
            quantity = item_info['quantity']
            price = product.get('member_price', product['price']) if is_vip else product['price']
            subtotal = price * quantity
            item_list.append({'product_id': product_id, 'name': product['name'], 'quantity': quantity, 'unit_price': price, 'subtotal': subtotal})
            total_price += subtotal

        # 4. Promotions and discounts
        is_first_pickup = self.is_first_time_pickup()

        # Show available promo codes
        show_promos = input("\nWould you like to see available promo codes? (y/n): ").strip().lower()
        if show_promos == 'y':
            self.show_available_promos()

        # Apply promo code (both pickup and delivery can use promo codes)
        promo_code = input("\nEnter promo code (or press Enter to skip): ").strip()
        if promo_code:
            promo_discount = self.apply_promo_code(promo_code, is_pickup, is_first_pickup, total_price)
            if promo_discount > 0:
                promo_code_used = promo_code
                # Mark first-time pickup if applicable
                if is_pickup and is_first_pickup and promo_code.upper() == 'NEWMONASH20':
                    self.set_pickup_flag()
            # Wait for user to read the promo code result message
            input("\nPress Enter to continue...")

        # Apply pickup discount for Monash students (cannot combine with promo)
        if is_pickup and is_monash and promo_discount == 0:
            pickup_discount = 0.05
            print("\n🎓 ✅ Monash Student Pickup Discount Applied: 5% off")

        # Set delivery fee
        if not is_pickup:
            if is_monash:
                delivery_fee = 0
                print("\n🎓 ✅ Monash Student Benefit: FREE Delivery (Save $20)")
            else:
                delivery_fee = 20

        # Only one discount applies (promo takes precedence)
        if pickup_discount > 0 and promo_discount > 0:
            print("\n⚠️  Note: Promo code discount applied instead of Monash pickup discount.")
            pickup_discount = 0

        discount_amount = 0
        if promo_discount > 0:
            discount_amount = total_price * promo_discount
        elif pickup_discount > 0:
            discount_amount = total_price * pickup_discount

        final_total = total_price - discount_amount + delivery_fee

        # 5. Funds validation
        funds = self.get_funds()
        print(f"\nOrder total: ${total_price:.2f}")
        if discount_amount > 0:
            print(f"Discount: -${discount_amount:.2f}")
        if delivery_fee > 0:
            print(f"Delivery Fee: +${delivery_fee:.2f}")
        print(f"Final total: ${final_total:.2f}")
        print(f"Your available funds: ${funds:.2f}")
        if funds < final_total:
            print("❌ Insufficient funds. Order failed.")
            print(f"💡 You need ${final_total - funds:.2f} more. Please top up your account.")
            input("\nPress Enter to continue...")
            return

        # 6. Order summary
        print("\n" + "="*60)
        print(" ORDER SUMMARY")
        print("="*60)
        print(f"Customer: {customer_name}")
        print(f"Email: {email}")
        if is_monash:
            print(f"Status: 🎓 Monash Student")
        print("\nItems:")
        for item in item_list:
            print(f"  • {item['name']} x{item['quantity']} @ ${item['unit_price']:.2f} = ${item['subtotal']:.2f}")

        print(f"\nSubtotal: ${total_price:.2f}")

        if is_pickup:
            print(f"\n📦 Pickup at:")
            print(f"   {pickup_store['name']}")
            print(f"   {pickup_store['address']}")
            print(f"   {pickup_store['phone']}")
            print(f"   Hours: {pickup_store['hours']}")
            if promo_code_used:
                print(f"\n🎟️  Promo Code: {promo_code_used} (-{int(promo_discount*100)}%)")
            elif pickup_discount > 0:
                print(f"\n🎓 Monash Student Pickup Discount: -5%")
        else:
            print(f"\n🚚 Delivery to: {delivery_address}")
            if is_monash:
                print(f"   Delivery Fee: FREE 🎓 (Regular: $20.00)")
            elif delivery_fee > 0:
                print(f"   Delivery Fee: ${delivery_fee:.2f}")

        if discount_amount > 0:
            print(f"\nDiscount: -${discount_amount:.2f}")
        if delivery_fee > 0:
            print(f"Delivery Fee: +${delivery_fee:.2f}")

        print(f"\n{'='*60}")
        print(f"TOTAL: ${final_total:.2f}")
        print("="*60)

        # 7. Order confirmation
        confirm = input("\n🛒 Confirm and place order? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\n❌ Order cancelled. Your cart has been preserved.")
            input("\nPress Enter to continue...")
            return

        # 8. Payment processing, inventory update, and order saving
        self.deduct_funds(final_total)
        self.update_inventory()
        # Save order
        try:
            from Order import Order as OrderManager
            order_manager = OrderManager()
            order_manager.create_order(
                user_email=email,
                product_list=item_list,
                total_price=final_total
            )
        except Exception as e:
            print(f"⚠️  Order saving failed: {e}")
        # Clear shopping cart
        self.cart.clear()
        print("\n✅ Order placed successfully! Thank you for shopping.")
        print("Your cart has been cleared. No modifications allowed post-checkout.")
        input("\nPress Enter to continue...")