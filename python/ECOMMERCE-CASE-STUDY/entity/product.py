# entity/product.py
from typing import Optional

class Product:
    """
    Entity class for 'products' table.
    Columns: product_id (PK), name, price, description, stockQuantity
    """

    def __init__(self,
                 product_id: Optional[int] = None,
                 name: Optional[str] = None,
                 price: Optional[float] = None,
                 description: Optional[str] = None,
                 stockQuantity: Optional[int] = None):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._description = description
        self._stockQuantity = stockQuantity

    # Getters
    def get_product_id(self) -> Optional[int]:
        return self._product_id

    def get_name(self) -> Optional[str]:
        return self._name

    def get_price(self) -> Optional[float]:
        return self._price

    def get_description(self) -> Optional[str]:
        return self._description

    def get_stockQuantity(self) -> Optional[int]:
        return self._stockQuantity

    # Setters
    def set_product_id(self, product_id: int) -> None:
        self._product_id = product_id

    def set_name(self, name: str) -> None:
        self._name = name

    def set_price(self, price: float) -> None:
        self._price = price

    def set_description(self, description: Optional[str]) -> None:
        self._description = description

    def set_stockQuantity(self, stockQuantity: int) -> None:
        self._stockQuantity = stockQuantity

    def __repr__(self) -> str:
        return f"Product(product_id={self._product_id}, name={self._name}, price={self._price}, stockQuantity={self._stockQuantity})"
