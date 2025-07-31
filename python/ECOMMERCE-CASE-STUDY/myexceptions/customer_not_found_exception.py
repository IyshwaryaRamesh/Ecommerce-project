# myexceptions/customer_not_found_exception.py

class CustomerNotFoundException(Exception):
    """
    Raised when a customer id does not exist in the database.
    Matches the case-study requirement to throw a user-defined exception
    if the user enters an invalid customer id.
    """

    def __init__(self, customer_id=None, message=None):
        if message is None:
            if customer_id is None:
                message = "Customer not found."
            else:
                message = f"Customer not found for id: {customer_id}"
        super().__init__(message)
        self.customer_id = customer_id
