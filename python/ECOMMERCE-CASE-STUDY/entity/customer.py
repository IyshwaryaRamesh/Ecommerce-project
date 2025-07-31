# entity/customer.py
from typing import Optional

class Customer:
    """
    Entity class for 'customers' table.
    Columns: customer_id (PK), name, email, password
    """

    def __init__(self,
                 customer_id: Optional[int] = None,
                 name: Optional[str] = None,
                 email: Optional[str] = None,
                 password: Optional[str] = None):
        # default + parameterized constructor
        self._customer_id = customer_id
        self._name = name
        self._email = email
        self._password = password

    # Getters
    def get_customer_id(self) -> Optional[int]:
        return self._customer_id

    def get_name(self) -> Optional[str]:
        return self._name

    def get_email(self) -> Optional[str]:
        return self._email

    def get_password(self) -> Optional[str]:
        return self._password

    # Setters
    def set_customer_id(self, customer_id: int) -> None:
        self._customer_id = customer_id

    def set_name(self, name: str) -> None:
        self._name = name

    def set_email(self, email: str) -> None:
        self._email = email

    def set_password(self, password: str) -> None:
        self._password = password

    def __repr__(self) -> str:
        return f"Customer(customer_id={self._customer_id}, name={self._name}, email={self._email})"
