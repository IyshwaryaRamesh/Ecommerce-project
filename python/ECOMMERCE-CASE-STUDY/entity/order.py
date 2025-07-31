# entity/order.py
from typing import Optional
from datetime import datetime

class Order:
    """
    Entity class for 'orders' table.
    Columns: order_id (PK), customer_id (FK), order_date, total_price, shipping_address
    """

    def __init__(self,
                 order_id: Optional[int] = None,
                 customer_id: Optional[int] = None,
                 order_date: Optional[datetime] = None,
                 total_price: Optional[float] = None,
                 shipping_address: Optional[str] = None):
        self._order_id = order_id
        self._customer_id = customer_id
        self._order_date = order_date
        self._total_price = total_price
        self._shipping_address = shipping_address

    # Getters
    def get_order_id(self) -> Optional[int]:
        return self._order_id

    def get_customer_id(self) -> Optional[int]:
        return self._customer_id

    def get_order_date(self) -> Optional[datetime]:
        return self._order_date

    def get_total_price(self) -> Optional[float]:
        return self._total_price

    def get_shipping_address(self) -> Optional[str]:
        return self._shipping_address

    # Setters
    def set_order_id(self, order_id: int) -> None:
        self._order_id = order_id

    def set_customer_id(self, customer_id: int) -> None:
        self._customer_id = customer_id

    def set_order_date(self, order_date: datetime) -> None:
        self._order_date = order_date

    def set_total_price(self, total_price: float) -> None:
        self._total_price = total_price

    def set_shipping_address(self, shipping_address: str) -> None:
        self._shipping_address = shipping_address

    def __repr__(self) -> str:
        return f"Order(order_id={self._order_id}, customer_id={self._customer_id}, order_date={self._order_date}, total_price={self._total_price})"
