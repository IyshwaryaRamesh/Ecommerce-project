# myexceptions/order_not_found_exception.py

class OrderNotFoundException(Exception):
    """
    Raised when an order id does not exist in the database.
    Required by the case-study to be thrown when an invalid order id is entered.
    """

    def __init__(self, order_id=None, message=None):
        if message is None:
            if order_id is None:
                message = "Order not found."
            else:
                message = f"Order not found for id: {order_id}"
        super().__init__(message)
        self.order_id = order_id
