# entity/cart.py
from typing import Optional

class Cart:
    """
    Entity class for 'cart' table.
    Columns: cart_id (PK), customer_id (FK), product_id (FK), quantity
    """

    def __init__(self,
                 cart_id: Optional[int] = None,
                 customer_id: Optional[int] = None,
                 product_id: Optional[int] = None,
                 quantity: Optional[int] = None):
        self._cart_id = cart_id
        self._customer_id = customer_id
        self._product_id = product_id
        self._quantity = quantity

    # Getters
    def get_cart_id(self) -> Optional[int]:
        return self._cart_id

    def get_customer_id(self) -> Optional[int]:
        return self._customer_id

    def get_product_id(self) -> Optional[int]:
        return self._product_id

    def get_quantity(self) -> Optional[int]:
        return self._quantity

    # Setters
    def set_cart_id(self, cart_id: int) -> None:
        self._cart_id = cart_id

    def set_customer_id(self, customer_id: int) -> None:
        self._customer_id = customer_id

    def set_product_id(self, product_id: int) -> None:
        self._product_id = product_id

    def set_quantity(self, quantity: int) -> None:
        self._quantity = quantity

    def __repr__(self) -> str:
        return f"Cart(cart_id={self._cart_id}, customer_id={self._customer_id}, product_id={self._product_id}, quantity={self._quantity})"
