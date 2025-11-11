"""
Product Module - Product entities, validation, and factory utilities.

Provides abstract/base product types with validated attributes, concrete subclasses
for general and food products, and a simple factory for (de)serialization.

Author: Applied10_Group6
Version: 1.0
"""
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union


class ProductValidator:
    """
    ProductValidator - Encapsulates validation rules for product fields.

    Provides reusable checks for numeric bounds, required strings, and
    category/subcategory constraints shared across product classes.

    Author: Applied10_Group6
    Version: 1.0
    """
    @staticmethod
    def validate_positive_number(value: Union[int, float], field_name: str) -> None:
        """
        Ensure a numeric field is non-negative.

        :param value: Number to validate.
        :param field_name: Field label for error messages.
        :raises ValueError: If value is not a number or is negative.
        """
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"{field_name} must be a positive number, got {value}")

    @staticmethod
    def validate_required_string(value: Any, field_name: str) -> None:
        """
        Ensure a required string is present and non-empty.

        :param value: Value to validate.
        :param field_name: Field label for error messages.
        :raises ValueError: If value is not a non-empty string.
        """
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} is required and cannot be empty")

    @staticmethod
    def validate_category(category: str, subcategory: str) -> None:
        """
        Ensure category/subcategory strings are valid.

        :param category: High-level category.
        :param subcategory: Specific subcategory.
        :raises ValueError: If either is invalid.
        """
        ProductValidator.validate_required_string(category, "Category")
        ProductValidator.validate_required_string(subcategory, "Subcategory")


class Product(ABC):
    """
    Product - Abstract base class for product entities.

    Defines validated core attributes (id, name, brand, description, category,
    subcategory, price, member_price, quantity) and the serialization interface
    to_dict()/from_dict()/__str__() for concrete subclasses.

    Author: Applied10_Group6
    Version: 1.0
    """

    def __init__(self, id: str, name: str, brand: str, description: str,
                 category: str, price: float, member_price: Optional[float] = None,
                 quantity: int = 0, subcategory: Optional[str] = None):
        """
        Construct a Product with validated core fields.

        :param id: Unique product identifier.
        :param name: Product display name.
        :param brand: Manufacturer/brand.
        :param description: Brief description.
        :param category: Top-level category.
        :param price: Regular price (>= 0).
        :param member_price: Member price (defaults to price).
        :param quantity: Inventory count (>= 0).
        :param subcategory: Optional subcategory label.
        :raises ValueError: On invalid fields.
        """
        # Validate inputs before setting private attributes
        ProductValidator.validate_required_string(id, "Product ID")
        ProductValidator.validate_required_string(name, "Product name")
        ProductValidator.validate_required_string(brand, "Brand")
        ProductValidator.validate_category(category, subcategory)
        ProductValidator.validate_positive_number(price, "Price")
        ProductValidator.validate_positive_number(quantity, "Quantity")

        # Use private attributes for encapsulation
        self.__id = id
        self.__name = name
        self.__brand = brand
        self.__description = description
        self.__category = category
        self.__subcategory = subcategory
        self.__price = float(price)
        self.__member_price = float(member_price) if member_price is not None else float(price)
        self.__quantity = int(quantity)

    # Property decorators for encapsulation - read-only properties
    @property
    def id(self) -> str:
        """
        Returns the unique product identifier.

        :return: Product ID.
        """
        return self.__id

    @property
    def name(self) -> str:
        """
        Returns the product display name.

        :return: Name string.
        """
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        """
        Sets the product display name.

        :param value: Non-empty name string.
        :raises ValueError: If value is empty/invalid.
        """
        ProductValidator.validate_required_string(value, "Product name")
        self.__name = value

    @property
    def brand(self) -> str:
        """
        Returns the brand/manufacturer.

        :return: Brand string.
        """
        return self.__brand

    @brand.setter
    def brand(self, value: str) -> None:
        """
        Sets the brand/manufacturer.

        :param value: Non-empty brand string.
        :raises ValueError: If value is empty/invalid.
        """
        ProductValidator.validate_required_string(value, "Brand")
        self.__brand = value

    @property
    def description(self) -> str:
        """
        Returns the short product description.

        :return: Description text.
        """
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        """
        Sets the product description.

        :param value: Free-text description.
        """
        self.__description = value

    @property
    def category(self) -> str:
        """
        Returns the top-level product category.

        :return: Category string.
        """
        return self.__category

    @property
    def subcategory(self) -> str:
        """
        Returns the optional subcategory.

        :return: Subcategory string or None-equivalent if unset.
        """
        return self.__subcategory

    @property
    def price(self) -> float:
        """
        Returns the regular price.

        :return: Price (>= 0).
        """
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        """
        Sets the regular price.

        :param value: Price (>= 0).
        :raises ValueError: If value is negative or not a number.
        """
        ProductValidator.validate_positive_number(value, "Price")
        self.__price = float(value)

    @property
    def member_price(self) -> float:
        """
        Returns the member price.

        :return: Member price (>= 0).
        """
        return self.__member_price

    @member_price.setter
    def member_price(self, value: float) -> None:
        """
        Sets the member price.

        :param value: Member price (>= 0).
        :raises ValueError: If value is negative or not a number.
        """
        ProductValidator.validate_positive_number(value, "Member price")
        self.__member_price = float(value)

    @property
    def quantity(self) -> int:
        """
        Returns the available stock.

        :return: Quantity (>= 0).
        """
        return self.__quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        """
        Sets the available stock.

        :param value: Quantity (>= 0).
        :raises ValueError: If value is negative or not a number.
        """
        ProductValidator.validate_positive_number(value, "Quantity")
        self.__quantity = int(value)

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the product to a JSON-ready dictionary.

        :return: Dict representation containing all persisted fields.
        """
        pass

    @staticmethod
    @abstractmethod
    def from_dict(data: Dict[str, Any]) -> 'Product':
        """
        Creates a concrete Product instance from a dictionary payload.

        :param data: Parsed JSON-like dictionary.
        :return: Concrete Product (subclass) instance.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns a human-readable multi-line summary for display/printing.

        :return: Multi-line string summary.
        """
        pass

class GeneralProduct(Product):
    """"
    GeneralProduct - Concrete product without food-specific metadata.

    Implements JSON-ready serialization and human-readable formatting for
    general merchandise items.

    Author: Applied10_Group6
    Version: 1.0
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize general product fields.

        :return: Dict representation of the product.
        """
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'price': self.price,
            'member_price': self.member_price,
            'quantity': self.quantity
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GeneralProduct':
        """
        Build a GeneralProduct from dict data.

        :param data: Parsed JSON-like dict.
        :return: GeneralProduct instance.
        :raises ValueError: On invalid fields.
        """
        return GeneralProduct(
            id=data.get('id'),
            name=data.get('name'),
            brand=data.get('brand'),
            description=data.get('description'),
            category=data.get('category'),
            price=data.get('price'),
            member_price=data.get('member_price'),
            quantity=data.get('quantity', 0),
            subcategory=data.get('subcategory')
        )

    def __str__(self) -> str:
        """
        Multi-line summary for display/printing.
        """
        return (f"ID: {self.id}\n"
                f"Name: {self.name}\n"
                f"Brand: {self.brand}\n"
                f"Category: {self.category}\n"
                f"Subcategory: {self.subcategory}\n"
                f"Price: ${self.price}\n"
                f"Member Price: ${self.member_price}\n"
                f"Quantity: {self.quantity}")

class FoodProduct(Product):
    """
    FoodProduct - Concrete product with food-specific metadata.

    Adds expiration date, ingredients, storage instructions, and allergens
    with input validation and extended serialization behavior.

    Author: Applied10_Group6
    Version: 1.0
    """

    def __init__(self, id: str, name: str, brand: str, description: str,
                 category: str, price: float, member_price: Optional[float] = None,
                 quantity: int = 0, expiration_date: Optional[str] = None,
                 ingredients: Optional[str] = None, storage_instructions: Optional[str] = None,
                 allergens: Optional[str] = None, subcategory: Optional[str] = None):
        """
        Construct a FoodProduct with additional food-related fields.

        :param expiration_date: Label string for expiry date.
        :param ingredients: Comma-separated ingredients.
        :param storage_instructions: Storage guidance.
        :param allergens: Allergen info ('' if none; not None).
        :raises ValueError: If required food fields are invalid.
        """
        super().__init__(id, name, brand, description, category, price, member_price, quantity, subcategory)

        # Validate food-specific required fields
        ProductValidator.validate_required_string(expiration_date, "Expiration date")
        ProductValidator.validate_required_string(ingredients, "Ingredients")
        ProductValidator.validate_required_string(storage_instructions, "Storage instructions")

        if allergens is None:
            raise ValueError("FoodProduct: allergens is required (can be empty string, but not None).")

        # Use private attributes for encapsulation
        self.__expiration_date = expiration_date
        self.__ingredients = ingredients
        self.__storage_instructions = storage_instructions
        self.__allergens = allergens

    # Property decorators for food-specific attributes
    @property
    def expiration_date(self) -> str:
        """
        Returns the expiration date label.

        :return: Expiration date string.
        """
        return self.__expiration_date

    @expiration_date.setter
    def expiration_date(self, value: str) -> None:
        """
        Sets the expiration date.

        :param value: Non-empty expiration date string.
        :raises ValueError: If value is empty/invalid.
        """
        ProductValidator.validate_required_string(value, "Expiration date")
        self.__expiration_date = value

    @property
    def ingredients(self) -> str:
        """
        Returns the ingredients listing.

        :return: Ingredients string.
        """
        return self.__ingredients

    @ingredients.setter
    def ingredients(self, value: str) -> None:
        """
        Sets the ingredients listing.

        :param value: Non-empty ingredients string.
        :raises ValueError: If value is empty/invalid.
        """
        ProductValidator.validate_required_string(value, "Ingredients")
        self.__ingredients = value

    @property
    def storage_instructions(self) -> str:
        """
        Returns the storage guidance text.

        :return: Storage instructions string.
        """
        return self.__storage_instructions

    @storage_instructions.setter
    def storage_instructions(self, value: str) -> None:
        """
        Sets the storage guidance text.

        :param value: Non-empty storage instructions.
        :raises ValueError: If value is empty/invalid.
        """
        ProductValidator.validate_required_string(value, "Storage instructions")
        self.__storage_instructions = value

    @property
    def allergens(self) -> str:
        """
        Returns allergen information.

        :return: Allergen string ('' means none).
        """
        return self.__allergens

    @allergens.setter
    def allergens(self, value: str) -> None:
        """
        Sets allergen information.

        :param value: Allergen string; '' means none (must not be None).
        :raises ValueError: If value is None.
        """
        if value is None:
            raise ValueError("Allergens cannot be None (use empty string for no allergens)")
        self.__allergens = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the food product to a JSON-ready dictionary (extends base fields).

        :return: Dict including base and food-specific fields.
        """
        d = super().to_dict()
        d.update({
            'expiration_date': self.expiration_date,
            'ingredients': self.ingredients,
            'storage_instructions': self.storage_instructions,
            'allergens': self.allergens
        })
        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FoodProduct':
        """
        Creates a FoodProduct from a dictionary payload.

        :param data: Parsed JSON-like dictionary.
        :return: FoodProduct instance.
        :raises ValueError: Propagated from validators on invalid fields.
        """
        return FoodProduct(
            id=data.get('id'),
            name=data.get('name'),
            brand=data.get('brand'),
            description=data.get('description'),
            category=data.get('category'),
            price=data.get('price'),
            member_price=data.get('member_price'),
            quantity=data.get('quantity', 0),
            expiration_date=data.get('expiration_date'),
            ingredients=data.get('ingredients'),
            storage_instructions=data.get('storage_instructions'),
            allergens=data.get('allergens'),
            subcategory=data.get('subcategory')
        )

    def __str__(self) -> str:
        """
        Returns a multi-line summary including food-specific fields.

        :return: Human-readable string.
        """
        info = super().__str__()
        info += (f"\nExpiration Date: {self.expiration_date}\n"
                 f"Ingredients: {self.ingredients}\n"
                 f"Allergens: {self.allergens}")
        return info


class ProductFactory:
    """
    ProductFactory - Factory utilities for product creation and persistence.

    Creates concrete product instances from dict payloads and loads/saves
    product collections to JSON files.

    Author: Applied10_Group6
    Version: 1.0
    """

    @staticmethod
    def create_product(data: Dict[str, Any]) -> Product:
        """
        Create appropriate product type from dict.

        :param data: Source dict (e.g., from JSON).
        :return: FoodProduct if food fields present; otherwise GeneralProduct.
        """
        # Determine product type by checking for food-specific fields
        if 'expiration_date' in data or 'ingredients' in data:
            return FoodProduct.from_dict(data)
        else:
            return GeneralProduct.from_dict(data)

    @staticmethod
    def create_products_from_file(filename: str) -> Dict[str, Product]:
        """
        Load products from a JSON file.

        :param filename: Input JSON path.
        :return: Dict of product_id -> Product (may be empty on error).
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            products = {}
            for product_id, product_data in data.items():
                try:
                    products[product_id] = ProductFactory.create_product(product_data)
                except Exception as e:
                    print(f"Warning: Could not load product {product_id}: {e}")

            return products
        except FileNotFoundError:
            print(f"Warning: File {filename} not found, returning empty product dict")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filename}: {e}")
            return {}

    @staticmethod
    def save_products_to_file(products: Dict[str, Product], filename: str) -> bool:
        """
        Save products to JSON file.

        Args:
            products: Dictionary mapping product IDs to Product instances
            filename: Path to JSON file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            products_dict = {pid: prod.to_dict() for pid, prod in products.items()}
            with open(filename, 'w') as f:
                json.dump(products_dict, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving products to {filename}: {e}")
            return False


if __name__ == '__main__':
    print("=== Demonstrating OOP Principles in Product Module ===\n")

    # Demo data: includes both electronics and food products
    products = [
        GeneralProduct('1', 'Laptop', 'Dell', 'High performance laptop', 'Electronics', 1200, 1100, 10, subcategory='Computers'),
        GeneralProduct('2', 'Smartphone', 'Apple', 'Latest model smartphone', 'Electronics', 800, 750, 25, subcategory='Phones'),
        GeneralProduct('3', 'Headphones', 'Sony', 'Noise cancelling headphones', 'Electronics', 150, 140, 50, subcategory='Audio'),
        GeneralProduct('4', 'Monitor', 'Samsung', '24-inch LED monitor', 'Electronics', 200, 180, 15, subcategory='Displays'),
        GeneralProduct('5', 'Keyboard', 'Logitech', 'Mechanical keyboard', 'Electronics', 90, 80, 30, subcategory='Accessories'),
        FoodProduct('6', 'Bread', 'Bakery', 'Freshly baked bread', 'Food', 5, 4.5, 50, '10/10/2025', 'Flour, Water, Yeast', 'Keep dry', 'Gluten', subcategory='Bakery'),
        FoodProduct('7', 'Milk', 'DairyPure', 'Whole milk', 'Food', 3, 2.8, 40, '15/10/2025', 'Milk', 'Refrigerate', 'Lactose', subcategory='Dairy'),
        FoodProduct('8', 'Eggs', 'FarmFresh', 'Free range eggs', 'Food', 6, 5.5, 60, '20/10/2025', 'Eggs', 'Refrigerate', 'Egg', subcategory='Dairy'),
        FoodProduct('9', 'Apple', 'Orchard', 'Fresh apple', 'Food', 2, 1.8, 100, '25/10/2025', 'Apple', 'Keep cool', '', subcategory='Fruit'),
        FoodProduct('10', 'Orange Juice', 'Tropicana', '100% pure orange juice', 'Food', 8, 7.5, 35, '30/10/2025', 'Orange', 'Refrigerate', '', subcategory='Beverage')
    ]

    # Demonstrate polymorphism - different product types use same interface
    print("1. POLYMORPHISM: All products have same interface")
    for p in products[:2]:  # Show first 2 for brevity
        print(p)
        print(f"Dict representation: {p.to_dict()}\n")

    # Demonstrate encapsulation - using property setters with validation
    print("2. ENCAPSULATION: Private attributes with validated setters")
    try:
        test_product = GeneralProduct('99', 'Test', 'Brand', 'Desc', 'Cat', 100, 90, 5, subcategory='Sub')
        print(f"Original price: ${test_product.price}")
        test_product.price = 120
        print(f"Updated price: ${test_product.price}")
        # This should fail due to validation
        test_product.price = -10
    except ValueError as e:
        print(f"Validation works! Error: {e}\n")

    # Demonstrate factory pattern
    print("3. FACTORY PATTERN: Using ProductFactory to create and save products")
    products_dict = {p.id: p for p in products}
    success = ProductFactory.save_products_to_file(products_dict, 'products.txt')
    print(f"Saved products: {success}")

    # Load products using factory
    loaded_products = ProductFactory.create_products_from_file('products.txt')
    print(f"Loaded {len(loaded_products)} products from file\n")

    # Demonstrate abstraction
    print("4. ABSTRACTION: Product is abstract, cannot be instantiated directly")
    print("   - GeneralProduct and FoodProduct implement abstract methods")
    print("   - ProductValidator abstracts validation logic")
    print("   - ProductFactory abstracts object creation\n")

    print("=== OOP Principles Successfully Demonstrated ===")
    print("✓ Encapsulation: Private attributes (__id, __name, etc.) with property decorators")
    print("✓ Inheritance: GeneralProduct and FoodProduct inherit from Product")
    print("✓ Abstraction: Product ABC, ProductValidator, ProductFactory")
    print("✓ Polymorphism: to_dict(), from_dict(), __str__() implemented differently")
