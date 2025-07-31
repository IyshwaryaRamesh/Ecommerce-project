# dao/order_processor_repository.py
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from entity.product import Product
from entity.customer import Customer

class OrderProcessorRepository(ABC):
    """
    Service Provider interface defined in the case-study.
    All methods interact with the database and return booleans/lists per the spec.
    """

    @abstractmethod
    def createProduct(self, product: Product) -> bool: ...
    @abstractmethod
    def createCustomer(self, customer: Customer) -> bool: ...

    @abstractmethod
    def deleteProduct(self, productId: int) -> bool: ...
    @abstractmethod
    def deleteCustomer(self, customerId: int) -> bool: ...

    @abstractmethod
    def addToCart(self, customer: Customer, product: Product, quantity: int) -> bool: ...
    @abstractmethod
    def removeFromCart(self, customer: Customer, product: Product) -> bool: ...

    @abstractmethod
    def getAllFromCart(self, customer: Customer) -> List[Tuple[Product, int]]: ...
        # Returns a list of (Product, quantity)

    @abstractmethod
    def placeOrder(
        self,
        customer: Customer,
        items: Optional[List[Tuple[Product, int]]],  # if None, use items from cart
        shippingAddress: str
    ) -> bool: ...

    @abstractmethod
    def getOrdersByCustomer(self, customerId: int):
        """
        Returns a list of entries for the customer's orders.
        Each entry includes order_id, order_date, Product, quantity.
        """
        ...
