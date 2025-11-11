"""
Cart Module - Shopping cart management system for the online supermarket.

This module provides comprehensive shopping cart functionality including item management,
validation, persistence, and filtering. It demonstrates key OOP principles through
encapsulation of cart logic, abstraction of business rules, and proper data validation.

Author: Applied10_Group6
Version: 1.0
"""

import json
from collections import OrderedDict
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class CartRules:
    """
    CartRules - Encapsulates business rules and constraints for the shopping cart.

    This class defines the maximum limits for cart items and product quantities,
    and provides validation methods to ensure these rules are enforced throughout
    the application.

    Author: Applied10_Group6
    Version: 1.0
    """
    MAX_CART_ITEMS: int = 20
    MAX_PRODUCT_QUANTITY: int = 10

    @classmethod
    def validate_cart_capacity(cls, current_items: int) -> bool:
        """
        Validates if the cart has capacity for more items.

        :param current_items: The current number of items in the cart.
        :return: True if cart can accept more items, False otherwise.
        """
        return current_items < cls.MAX_CART_ITEMS

    @classmethod
    def validate_product_quantity(cls, quantity: int) -> bool:
        """
        Validates if the product quantity is within allowed limits.

        :param quantity: The quantity to validate.
        :return: True if quantity is valid (1-10), False otherwise.
        """
        return 0 < quantity <= cls.MAX_PRODUCT_QUANTITY


class CartItem:
    """
    CartItem - Represents a single item in the shopping cart.

    This class encapsulates the details of a cart item, including the product ID
    and quantity. It provides properties for accessing and modifying these attributes
    with built-in validation to ensure data integrity.

    Author: Applied10_Group6
    Version: 1.0
    """
    def __init__(self, product_id: str, quantity: int):
        """
        Constructs a CartItem with the specified product and quantity.

        :param product_id: The unique identifier of the product.
        :param quantity: The quantity of the product (must be 1-10).
        :raises ValueError: If quantity is not within valid range.
        """
        if not CartRules.validate_product_quantity(quantity):
            raise ValueError(f"Quantity must be between 1 and {CartRules.MAX_PRODUCT_QUANTITY}")
        self.__product_id = product_id
        self.__quantity = quantity

    @property
    def product_id(self) -> str:
        """
        Returns the product ID of this cart item.

        :return: The product ID.
        """
        return self.__product_id

    @property
    def quantity(self) -> int:
        """
        Returns the quantity of this cart item.

        :return: The quantity.
        """
        return self.__quantity

    @quantity.setter
    def quantity(self, value: int):
        """
        Sets the quantity of this cart item with validation.

        :param value: The new quantity value.
        :raises ValueError: If quantity is not within valid range.
        """
        if not CartRules.validate_product_quantity(value):
            raise ValueError(f"Quantity must be between 1 and {CartRules.MAX_PRODUCT_QUANTITY}")
        self.__quantity = value

    def add_quantity(self, amount: int) -> bool:
        """
        Adds to the current quantity if within limits.

        :param amount: The amount to add to the current quantity.
        :return: True if successful, False if would exceed limit.
        """
        new_qty = self.__quantity + amount
        if not CartRules.validate_product_quantity(new_qty):
            return False
        self.__quantity = new_qty
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the cart item to a dictionary representation.

        :return: Dictionary containing product_id and quantity.
        """
        return {'product_id': self.__product_id, 'quantity': self.__quantity}


class ShoppingCart:
    """
    ShoppingCart - Manages shopping carts for all users in the system.

    This class provides comprehensive cart management functionality including adding,
    removing, editing, and viewing cart items. It persists cart data to files and
    maintains the order of items as they are added. The class supports filtering
    cart contents and clearing carts on user logout.

    Author: Applied10_Group6
    Version: 1.0
    """

    def filter_cart(self, user_email: str, products: Dict, name: Optional[str] = None,
                   brand: Optional[str] = None, category: Optional[str] = None,
                   min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Dict]:
        """
        Filters cart items based on various criteria.

        :param user_email: The user's email address.
        :param products: Dictionary of all available products.
        :param name: Optional filter by product name.
        :param brand: Optional filter by product brand.
        :param category: Optional filter by product category.
        :param min_price: Optional minimum price filter.
        :param max_price: Optional maximum price filter.
        :return: List of filtered cart items with product details.
        """
        filtered = []
        cart_items = self.get_cart(user_email)

        for pid, qty in cart_items.items():
            product = products.get(pid)
            if not product:
                continue

            prod_dict = product.to_dict() if hasattr(product, 'to_dict') else product

            # Apply filters
            if name and name.lower() not in prod_dict['name'].lower():
                continue
            if brand and brand.lower() not in prod_dict['brand'].lower():
                continue
            if category and category.lower() != prod_dict['category'].lower():
                continue

            price = prod_dict.get('promotion_price', prod_dict['price'])
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue

            filtered.append({'product': prod_dict, 'quantity': qty})
        return filtered
    def __init__(self, filename: str = 'carts.txt'):
        """
        Constructs a ShoppingCart with file-based persistence.

        :param filename: The file name to store cart data (default: 'carts.txt').
        """
        self.__filename = filename  # Private attribute (encapsulation)
        self.__carts: Dict[str, OrderedDict] = {}  # Private attribute
        self.__cart_order: Dict[str, List[str]] = {}  # Track addition order
        self.__load_carts()

    @property
    def filename(self) -> str:
        """
        Returns the filename used for cart data storage.

        :return: The cart data filename.
        """
        return self.__filename

    def __load_carts(self):
        """
        Loads cart data from the storage file.

        This private method reads cart data and order information from JSON files.
        If files don't exist or are corrupted, it starts with empty carts.
        """
        try:
            with open(self.__filename, 'r') as f:
                data = json.load(f)
                for user, items in data.items():
                    self.__carts[user] = OrderedDict(items)
        except FileNotFoundError:
            print(f"Warning: {self.__filename} not found, starting with empty carts.")
        except json.JSONDecodeError:
            print(f"Error: {self.__filename} is invalid, starting with empty carts.")

        try:
            with open(self.__filename + '.order', 'r') as f:
                self.__cart_order = json.load(f)
        except Exception:
            pass

    def __save_carts(self):
        """
        Saves cart data to the storage file.

        This private method persists both cart contents and item order
        information to JSON files for data persistence.
        """
        with open(self.__filename, 'w') as f:
            json.dump(self.__carts, f, indent=4)
        with open(self.__filename + '.order', 'w') as f:
            json.dump(self.__cart_order, f, indent=4)

    def add_to_cart(self, user_email: str, product_id: str, quantity: int) -> bool:
        """
        Adds a product to the user's cart with validation.

        :param user_email: The user's email address.
        :param product_id: The unique identifier of the product.
        :param quantity: The quantity to add.
        :return: True if product was successfully added, False otherwise.
        """
        # Initialize cart if doesn't exist
        if user_email not in self.__carts:
            self.__carts[user_email] = OrderedDict()
            self.__cart_order[user_email] = []

        # Check if product already in cart
        if product_id in self.__carts[user_email]:
            new_qty = self.__carts[user_email][product_id] + quantity
            if not CartRules.validate_product_quantity(new_qty):
                print(f"Cannot add more than {CartRules.MAX_PRODUCT_QUANTITY} of a single product.")
                return False
            self.__carts[user_email][product_id] = new_qty
        else:
            # Check cart capacity
            if not CartRules.validate_cart_capacity(len(self.__carts[user_email])):
                print(f"Cannot have more than {CartRules.MAX_CART_ITEMS} items in the cart.")
                return False
            if not CartRules.validate_product_quantity(quantity):
                print(f"Invalid quantity: {quantity}")
                return False
            self.__carts[user_email][product_id] = quantity
            self.__cart_order[user_email].append(product_id)

        self.__save_carts()
        print(f"Added {quantity} of product {product_id} to {user_email}'s cart.")
        return True

    def remove_from_cart(self, user_email: str, product_id: str) -> bool:
        """
        Removes a product from the user's cart.

        :param user_email: The user's email address.
        :param product_id: The unique identifier of the product to remove.
        :return: True if product was successfully removed, False otherwise.
        """
        if user_email in self.__carts and product_id in self.__carts[user_email]:
            del self.__carts[user_email][product_id]
            if user_email in self.__cart_order and product_id in self.__cart_order[user_email]:
                self.__cart_order[user_email].remove(product_id)
            self.__save_carts()
            print(f"Removed product {product_id} from {user_email}'s cart.")
            return True
        print(f"Product {product_id} not found in {user_email}'s cart.")
        return False

    def view_cart(self, user_email: str, products: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Views the cart contents with detailed information.

        :param user_email: The user's email address.
        :param products: Optional product dictionary to include detailed product information.
        :return: List of cart items with product details and pricing.
        """
        if user_email not in self.__carts or not self.__carts[user_email]:
            print(f"No cart found for {user_email}.")
            return []

        cart_items = self.__carts[user_email]
        order = self.__cart_order.get(user_email, list(cart_items.keys()))
        result = []
        total_price = 0.0

        for pid in order:
            qty = cart_items.get(pid, 0)
            if qty == 0:
                continue

            prod = products[pid] if products and pid in products else None
            name = prod.name if prod and hasattr(prod, 'name') else pid
            price = prod.member_price if prod and hasattr(prod, 'member_price') else 0.0
            item_total = price * qty
            total_price += item_total

            result.append({
                'product_id': pid,
                'name': name,
                'quantity': qty,
                'individual_price': price,
                'total_price': item_total
            })

        print("\n--- Cart Items (ordered by addition) ---")
        for item in result:
            print(f"Product: {item['name']} | Quantity: {item['quantity']} | "
                  f"Price: ${item['individual_price']:.2f} | Total: ${item['total_price']:.2f}")
        print(f"Cart Total: ${total_price:.2f}")
        return result

    def clear_cart(self, user_email: str):
        """
        Clears all items from the user's cart.

        :param user_email: The user's email address.
        """
        if user_email in self.__carts:
            self.__carts[user_email] = OrderedDict()
            self.__cart_order[user_email] = []
            self.__save_carts()
            print(f"Cleared cart for {user_email}.")
        else:
            print(f"No cart found for {user_email}.")

    def get_cart(self, user_email: str) -> OrderedDict:
        """
        Returns the cart contents for the specified user.

        :param user_email: The user's email address.
        :return: OrderedDict containing the user's cart items.
        """
        if user_email in self.__carts:
            return self.__carts[user_email]
        print(f"No cart found for {user_email}. please create one first.")
        return OrderedDict()

    def edit_cart(self, user_email: str, product_id: str, new_quantity: int) -> bool:
        """
        Edits the quantity of a product in the user's cart.

        :param user_email: The user's email address.
        :param product_id: The unique identifier of the product.
        :param new_quantity: The new quantity to set (0 removes the item).
        :return: True if edit was successful, False otherwise.
        """
        if user_email not in self.__carts or product_id not in self.__carts[user_email]:
            print(f"Product {product_id} not found in {user_email}'s cart.")
            return False

        if new_quantity <= 0:
            return self.remove_from_cart(user_email, product_id)

        if not CartRules.validate_product_quantity(new_quantity):
            print(f"Cannot set quantity greater than {CartRules.MAX_PRODUCT_QUANTITY}.")
            return False

        self.__carts[user_email][product_id] = new_quantity
        self.__save_carts()
        print(f"Updated {product_id} quantity to {new_quantity} in {user_email}'s cart.")
        return True

    def session_logout(self, user_email: str):
        """
        Clears the user's cart upon logout or application close.

        :param user_email: The user's email address.
        """
        self.clear_cart(user_email)
        print(f"Cart cleared for {user_email} on logout or app close.")



# Alias for backward compatibility
Cart = ShoppingCart


if __name__ == '__main__':
    # Demonstration of OOP principles
    cart_manager = ShoppingCart()

    # Test encapsulation and validation
    print("=== Testing Cart Functionality ===")
    cart_manager.add_to_cart('test@monash.edu', '1', 2)
    cart_manager.add_to_cart('test@monash.edu', '2', 3)
    cart_manager.edit_cart('test@monash.edu', '1', 5)

    # Test viewing cart
    cart_manager.view_cart('test@monash.edu', products={
        '1': type('P', (), {'name': 'Laptop', 'member_price': 1000})(),
        '2': type('P', (), {'name': 'Phone', 'member_price': 500})()
    })

    # Test removal and clearing
    cart_manager.remove_from_cart('test@monash.edu', '1')
    cart_manager.clear_cart('test@monash.edu')
    cart_manager.session_logout('test@monash.edu')

    print("\n=== OOP Principles Demonstrated ===")
    print("1. Encapsulation: Private attributes (__carts, __cart_order)")
    print("2. Abstraction: CartRules class abstracts business logic")
    print("3. Validation: CartRules validates inputs before processing")
    print("4. Type Hints: Clear interfaces with type annotations")
