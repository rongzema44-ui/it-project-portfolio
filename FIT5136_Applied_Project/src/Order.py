"""
OrderStatus - Represents possible states of an order.

This enumeration encapsulates order states for consistent use throughout
the system and simplifies status validation.

Author: Tao Pan
Version: 2.0
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    """
    OrderStatus - Represents possible states of an order.

    This enumeration encapsulates order states for consistent use throughout
    the system and simplifies status validation.

    Author: Tao Pan
    Version: 1.0
    """
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class DataPersistence(ABC):
    """
    DataPersistence - Abstract base class for persistent data storage.

    This abstract class defines the structure for loading and saving data,
    ensuring consistent persistence logic across subclasses.

    Author: Tao Pan
    Version: 4.0
    """
    def __init__(self, filename: str):
        """
        Initializes the data persistence system.

        :param filename: The file name used for data storage.
        """
        self._filename = filename 
        self._data = self._load_data()

    @abstractmethod
    def _load_data(self) -> Dict[str, Any]:
        """
        Abstract method to load data from storage.


        :return: Dictionary representing stored data.
        """
        pass

    @abstractmethod
    def _save_data(self):
        """
        Abstract method to save data to storage.
        """
        pass

    @property
    def filename(self) -> str:
        """
        Returns the file name used for data persistence.

        :return: The storage file name.
        """
        return self._filename


class OrderData:
    """
    OrderData - Represents a single user order.

    This class encapsulates all order information including ID, user, product list,
    total price, status, and creation time, providing access through validated
    properties for data integrity.

    Author: Tao Pan
    Version: 2.0
    """
    def __init__(self, order_id: str, user_email: str, product_list: List[Dict],
                 total_price: float, status: OrderStatus = OrderStatus.PENDING):
        """
        Constructs an OrderData object.

        :param order_id: Unique identifier for the order.
        :param user_email: Email of the user who placed the order.
        :param product_list: List of ordered products (dict format).
        :param total_price: Total cost of the order.
        :param status: Current order status (default: Pending).
        """
        self.__order_id = order_id
        self.__user_email = user_email
        self.__product_list = product_list
        self.__total_price = total_price
        self.__status = status
        self.__created_at = datetime.now()

    # Encapsulation: Property decorators for controlled access
    @property
    def order_id(self) -> str:
        """
        Returns the order ID.

        :return: Order identifier string.
        """
        return self.__order_id

    @property
    def user_email(self) -> str:
        """
        Returns the user's email associated with this order.

        :return: User's email address.
        """
        return self.__user_email

    @property
    def product_list(self) -> List[Dict]:
        """
        Returns a copy of the product list to preserve data integrity.

        :return: A copy of the list of ordered products.
        """
        return self.__product_list.copy()  # Return copy to protect internal state

    @property
    def total_price(self) -> float:
        """
        Returns the total price of the order.

        :return: Total price as a float.
        """
        return self.__total_price

    @property
    def status(self) -> OrderStatus:
        """
        Returns the current order status.

        :return: The order status as an OrderStatus enum.
        """
        return self.__status

    @status.setter
    def status(self, value: OrderStatus):
        """
        Sets the order status with validation.

        :param value: The new order status.
        :raises TypeError: If value is not an OrderStatus enum.
        """
        if not isinstance(value, OrderStatus):
            raise TypeError("Status must be an OrderStatus enum")
        self.__status = value

    @property
    def created_at(self) -> datetime:
        """
        Returns the creation time of the order.

        :return: Datetime object of order creation.
        """
        return self.__created_at

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the order into a serializable dictionary.

        :return: Dictionary representation of the order.
        """
        return {
            'order_id': self.__order_id,
            'user_email': self.__user_email,
            'product_list': self.__product_list,
            'total_price': self.__total_price,
            'status': self.__status.value,
            'created_at': self.__created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderData':
        """
        Creates an OrderData object from a dictionary.

        :param data: Dictionary containing order data.
        :return: An OrderData instance.
        """
        order = cls.__new__(cls)
        order.__order_id = data.get('order_id')
        order.__user_email = data.get('user_email')
        order.__product_list = data.get('product_list', [])
        order.__total_price = data.get('total_price', 0.0)
        order.__status = OrderStatus(data.get('status', 'Pending'))
        created_str = data.get('created_at')
        order.__created_at = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S') if created_str else datetime.now()
        return order


class OrderManager(DataPersistence):
    """
    OrderManager - Handles all operations related to order management.

    This class inherits from DataPersistence and provides implementations for
    loading, saving, creating, updating, and listing orders. It demonstrates
    inheritance and polymorphism by overriding abstract methods.

    Author: Tao Pan
    Version: 2.0
    """
    def __init__(self, filename: str = 'orders.txt'):
        """
        Constructs an OrderManager with persistent storage.

        :param filename: The file name used to store order data.
        """
        super().__init__(filename)
        self.__orders: Dict[str, OrderData] = {}  # Private attribute
        self.__load_orders()

    def _load_data(self) -> Dict[str, Any]:
        """
        Loads order data from JSON storage.

        :return: Dictionary of raw order data.
        """
        try:
            with open(self._filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self._filename} not found, starting with empty orders.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: {self._filename} is corrupted, starting with empty orders.")
            return {}

    def _save_data(self):
        """
        Saves all order data to JSON storage.
        """
        data = {oid: order.to_dict() for oid, order in self.__orders.items()}
        with open(self._filename, 'w') as f:
            json.dump(data, f, indent=4)

    def __load_orders(self):
        """
        Loads OrderData objects into memory from stored data.
        """
        for order_id, order_data in self._data.items():
            self.__orders[order_id] = OrderData.from_dict(order_data)

    def create_order(self, user_email: str, product_list: List[Dict],
                    total_price: float) -> OrderData:
        """
        Creates and saves a new order for a user.

        :param user_email: The email address of the user placing the order.
        :param product_list: The list of ordered products.
        :param total_price: The total cost of the order.
        :return: The created OrderData instance.
        """
        order_id = str(len(self.__orders) + 1)
        order = OrderData(order_id, user_email, product_list, total_price)
        self.__orders[order_id] = order
        self._save_data()
        print(f"Order {order_id} created successfully.")
        return order

    def get_order(self, order_id: str) -> Optional[OrderData]:
        """
        Retrieves an order by its ID.

        :param order_id: The order's unique identifier.
        :return: Corresponding OrderData instance, or None if not found.
        """
        return self.__orders.get(order_id)

    def list_orders(self, user_email: Optional[str] = None) -> List[OrderData]:
        """
        Lists all orders, optionally filtered by a user's email.

        :param user_email: Optional filter by user email.
        :return: List of OrderData objects.
        """
        if user_email:
            return [order for order in self.__orders.values()
                   if order.user_email == user_email]
        return list(self.__orders.values())

    def update_order_status(self, order_id: str, status: OrderStatus):
        """
        Updates the status of an existing order.

        :param order_id: The unique identifier of the order.
        :param status: The new status to set for the order.
        """
        if order_id in self.__orders:
            self.__orders[order_id].status = status
            self._save_data()
            print(f"Order {order_id} status updated to {status.value}.")
        else:
            print(f"Order {order_id} not found.")


# Alias for backward compatibility
Order = OrderManager


if __name__ == '__main__':
    order_manager = Order()

    order_manager.create_order('test@monash.edu', [{'product_id': '1', 'quantity': 2}], 50)

    print(order_manager.get_order('1'))

    print(order_manager.list_orders())