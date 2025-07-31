# entity/order_item.py
from typing import Optional

class OrderItem:
    """
    Entity class for 'order_items' table.
    Columns: order_item_id (PK), order_id (FK), product_id (FK), quantity
    """

    def __init__(self,
                 order_item_id: Optional[int] = None,
                 order_id: Optional[int] = None,
                 product_id: Optional[int] = None,
                 quantity: Optional[int] = None):
        self._order_item_id = order_item_id
        self._order_id = order_id
        self._product_id = product_id
        self._quantity = quantity

    # Getters
    def get_order_item_id(self) -> Optional[int]:
        return self._order_item_id

    def get_order_id(self) -> Optional[int]:
        return self._order_id

    def get_product_id(self) -> Optional[int]:
        return self._product_id

    def get_quantity(self) -> Optional[int]:
        return self._quantity

    # Setters
    def set_order_item_id(self, order_item_id: int) -> None:
        self._order_item_id = order_item_id

    def set_order_id(self, order_id: int) -> None:
        self._order_id = order_id

    def set_product_id(self, product_id: int) -> None:
        self._product_id = product_id

    def set_quantity(self, quantity: int) -> None:
        self._quantity = quantity

    def __repr__(self) -> str:
        return f"OrderItem(order_item_id={self._order_item_id}, order_id={self._order_id}, product_id={self._product_id}, quantity={self._quantity})"
