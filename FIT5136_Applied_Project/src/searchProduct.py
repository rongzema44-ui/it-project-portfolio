"""
SearchProduct Module - Product search functionality with strategy pattern implementation.

This module provides flexible product search capabilities using the Strategy Pattern.
It demonstrates key OOP principles through abstraction of search strategies, encapsulation
of product data, and polymorphic search execution methods.

Author: Applied10_Group6
Version: 1.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SearchStrategy(ABC):
    """
    SearchStrategy - Abstract base class defining the interface for product search strategies.

    This class establishes the contract that all concrete search strategy implementations
    must follow, enabling polymorphic search behavior through the Strategy Pattern.

    """
    @abstractmethod
    def execute(self, products: Dict[str, Any], **criteria) -> List[Dict[str, Any]]:
        """
        Executes a search operation based on specific criteria.

        This abstract method must be implemented by all concrete strategy classes
        to define their specific search logic and filtering rules.

        :param products: Dictionary of products to search through.
        :param criteria: Search criteria specific to each strategy implementation.
        :return: List of product dictionaries matching the search criteria.
        """
        pass


class NameSearchStrategy(SearchStrategy):
    """
    NameSearchStrategy - Concrete strategy for searching products by name.

    This strategy performs case-insensitive partial matching on product names,
    allowing users to find products even with incomplete name input.

    """
    def execute(self, products: Dict[str, Any], **criteria) -> List[Dict[str, Any]]:
        """
        Searches products by name using case-insensitive partial matching.

        :param products: Dictionary of products to search through.
        :param criteria: Must contain 'name' key with search term.
        :return: List of products whose names contain the search term.
        """
        name = criteria.get('name', '')
        return [p for p in products.values() if name.lower() in p['name'].lower()]


class BrandSearchStrategy(SearchStrategy):
    """
    BrandSearchStrategy - Concrete strategy for searching products by brand.

    This strategy performs case-insensitive partial matching on product brands,
    enabling users to filter products by manufacturer or brand name.

    """
    def execute(self, products: Dict[str, Any], **criteria) -> List[Dict[str, Any]]:
        """
        Searches products by brand using case-insensitive partial matching.

        :param products: Dictionary of products to search through.
        :param criteria: Must contain 'brand' key with search term.
        :return: List of products whose brands contain the search term.
        """
        brand = criteria.get('brand', '')
        return [p for p in products.values() if brand.lower() in p['brand'].lower()]


class CategorySearchStrategy(SearchStrategy):
    """
    CategorySearchStrategy - Concrete strategy for searching products by category.

    This strategy performs case-insensitive exact matching on product categories,
    allowing users to browse all products within a specific category.

    """
    def execute(self, products: Dict[str, Any], **criteria) -> List[Dict[str, Any]]:
        """
        Searches products by category using case-insensitive exact matching.

        :param products: Dictionary of products to search through.
        :param criteria: Must contain 'category' key with exact category name.
        :return: List of products in the specified category.
        """
        category = criteria.get('category', '')
        return [p for p in products.values() if category.lower() == p['category'].lower()]


class PriceRangeSearchStrategy(SearchStrategy):
    """
    PriceRangeSearchStrategy - Concrete strategy for searching products by price range.

    This strategy filters products within a specified minimum and maximum price range,
    enabling users to find products that fit their budget.

    """
    def execute(self, products: Dict[str, Any], **criteria) -> List[Dict[str, Any]]:
        """
        Searches products within a specified price range.

        :param products: Dictionary of products to search through.
        :param criteria: Must contain 'min_price' and/or 'max_price' keys.
        :return: List of products with prices within the specified range.
        """
        min_price = criteria.get('min_price', 0)
        max_price = criteria.get('max_price', float('inf'))
        return [p for p in products.values() if min_price <= p['price'] <= max_price]


class SearchProduct:
    """
    SearchProduct - Main product search manager using Strategy Pattern.

    This class manages product search operations by encapsulating product data
    and providing a flexible search interface through interchangeable search strategies.
    It demonstrates encapsulation, composition, and polymorphism in action.

    """
    def __init__(self, products: Dict[str, Any]):
        """
        Constructs a SearchProduct instance with product data.

        :param products: Dictionary mapping product IDs to product information.
        """
        self.__products = products  # Private attribute (encapsulation)
        self.__search_strategy: SearchStrategy = None  # Composition

    @property
    def products(self) -> Dict[str, Any]:
        """
        Returns the encapsulated products dictionary.

        :return: Dictionary of all products.
        """
        return self.__products

    @products.setter
    def products(self, value: Dict[str, Any]):
        """
        Sets the products dictionary with validation.

        :param value: New products dictionary.
        :raises ValueError: If value is not a dictionary.
        """
        if not isinstance(value, dict):
            raise ValueError("Products must be a dictionary")
        self.__products = value

    def set_search_strategy(self, strategy: SearchStrategy):
        """
        Sets the search strategy to be used for the next search operation.

        :param strategy: A concrete SearchStrategy instance.
        :raises TypeError: If strategy is not an instance of SearchStrategy.
        """
        if not isinstance(strategy, SearchStrategy):
            raise TypeError("Strategy must be an instance of SearchStrategy")
        self.__search_strategy = strategy

    def search(self, **criteria) -> List[Dict[str, Any]]:
        """
        Executes a search using the currently set search strategy.

        This method demonstrates polymorphism by delegating the search operation
        to the concrete strategy implementation.

        :param criteria: Search criteria passed to the strategy.
        :return: List of products matching the search criteria.
        :raises ValueError: If no search strategy has been set.
        """
        if self.__search_strategy is None:
            raise ValueError("Search strategy not set")
        results = self.__search_strategy.execute(self.__products, **criteria)
        self.display_results(results)
        return results

    def search_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Searches for products by name.

        :param name: Product name or partial name to search for.
        :return: List of products matching the name criteria.
        """
        self.set_search_strategy(NameSearchStrategy())
        return self.search(name=name)

    def search_by_brand(self, brand: str) -> List[Dict[str, Any]]:
        """
        Searches for products by brand.

        :param brand: Brand name or partial brand name to search for.
        :return: List of products matching the brand criteria.
        """
        self.set_search_strategy(BrandSearchStrategy())
        return self.search(brand=brand)

    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Searches for products by category.

        :param category: Exact category name to search for.
        :return: List of products in the specified category.
        """
        self.set_search_strategy(CategorySearchStrategy())
        return self.search(category=category)

    def search_by_price_range(self, min_price: float, max_price: float) -> List[Dict[str, Any]]:
        """
        Searches for products within a specified price range.

        :param min_price: Minimum price threshold.
        :param max_price: Maximum price threshold.
        :return: List of products within the price range.
        """
        self.set_search_strategy(PriceRangeSearchStrategy())
        return self.search(min_price=min_price, max_price=max_price)

    def display_results(self, results: List[Dict[str, Any]]):
        """
        Displays search results in a formatted table.

        :param results: List of product dictionaries to display.
        """
        if not results:
            print("No products found.")
            return
        print("\n--- Search Results ---")
        for p in results:
            member_price = p.get('member_price', p['price'])
            print(f"ID: {p['id']} | Name: {p['name']} | Brand: {p['brand']} | "
                  f"Category: {p['category']} | Price: ${p['price']} | Member Price: ${member_price} | Quantity: {p['quantity']}")
        print("-" * 20)


if __name__ == '__main__':
    # Demonstration of SearchProduct functionality and OOP principles
    print("=== Demonstrating Product Search with Strategy Pattern ===\n")

    # Sample product data
    products = {
        '1': {'id': '1', 'name': 'Laptop', 'brand': 'Dell', 'category': 'Electronics', 'price': 1200, 'quantity': 10},
        '2': {'id': '2', 'name': 'Smartphone', 'brand': 'Apple', 'category': 'Electronics', 'price': 800, 'quantity': 25},
        '3': {'id': '3', 'name': 'Bread', 'brand': 'Bakery', 'category': 'Food', 'price': 5, 'quantity': 50}
    }

    # Create SearchProduct instance
    sp = SearchProduct(products)

    # Demonstrate different search strategies
    print("1. SEARCHING BY NAME:")
    sp.search_by_name('Laptop')

    print("\n2. SEARCHING BY BRAND:")
    sp.search_by_brand('Apple')

    print("\n3. SEARCHING BY CATEGORY:")
    sp.search_by_category('Food')

    print("\n4. SEARCHING BY PRICE RANGE:")
    sp.search_by_price_range(100, 1300)
