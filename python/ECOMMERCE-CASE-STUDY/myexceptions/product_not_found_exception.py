# myexceptions/product_not_found_exception.py

class ProductNotFoundException(Exception):
    """
    Raised when a product id does not exist in the database.
    Required by the case-study to be thrown when an invalid product id is entered.
    """

    def __init__(self, product_id=None, message=None):
        if message is None:
            if product_id is None:
                message = "Product not found."
            else:
                message = f"Product not found for id: {product_id}"
        super().__init__(message)
        self.product_id = product_id
