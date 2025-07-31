# main/ecom_app.py
from typing import List, Tuple, Dict, Any
from dao import OrderProcessorRepositoryImpl
from entity.customer import Customer
from entity.product import Product
from myexceptions import (
    CustomerNotFoundException,
    ProductNotFoundException,
    OrderNotFoundException,
)

# ---------- small input helpers ----------
def _prompt_nonempty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Input cannot be empty. Please try again.")

def _prompt_int(prompt: str, min_val: int = None) -> int:
    while True:
        try:
            v = int(input(prompt).strip())
            if min_val is not None and v < min_val:
                print(f"Enter a number >= {min_val}.")
                continue
            return v
        except ValueError:
            print("Please enter a valid integer.")

def _prompt_float(prompt: str, min_val: float = None) -> float:
    while True:
        try:
            v = float(input(prompt).strip())
            if min_val is not None and v < min_val:
                print(f"Enter a number >= {min_val}.")
                continue
            return v
        except ValueError:
            print("Please enter a valid number.")

def _print_line(ch: str = "-", width: int = 60):
    print(ch * width)


class EcomApp:
    """
    Menu-driven CLI that uses OrderProcessorRepositoryImpl to perform actions.

    Menu (7 items):
      1) Register Customer
      2) Create Product
      3) Delete Product
      4) Add to Cart
      5) View Cart
      6) Place Order
      7) View Customer Order
      0) Exit
    """

    def __init__(self, prop_file: str = "config/db.properties"):
        self.repo = OrderProcessorRepositoryImpl(prop_file)

    # -------- menu handlers --------

    def _register_customer(self):
        print("\n-- Register Customer --")
        name = _prompt_nonempty("Name: ")
        email = _prompt_nonempty("Email: ")
        password = _prompt_nonempty("Password: ")
        cust = Customer(name=name, email=email, password=password)
        try:
            ok = self.repo.createCustomer(cust)
            if ok:
                print(f"Customer created with ID: {cust.get_customer_id()}")
        except Exception as e:
            print("Failed to create customer:", e)

    def _create_product(self):
        print("\n-- Create Product --")
        name = _prompt_nonempty("Product name: ")
        price = _prompt_float("Price: ", min_val=0.0)
        desc = input("Description (optional): ").strip() or None
        stock = _prompt_int("Stock quantity: ", min_val=0)
        prod = Product(name=name, price=price, description=desc, stockQuantity=stock)
        try:
            ok = self.repo.createProduct(prod)
            if ok:
                print(f"Product created with ID: {prod.get_product_id()}")
        except Exception as e:
            print("Failed to create product:", e)

    def _delete_product(self):
        print("\n-- Delete Product --")
        pid = _prompt_int("Product ID to delete: ", min_val=1)
        try:
            ok = self.repo.deleteProduct(pid)
            if ok:
                print(f"Product {pid} deleted.")
        except ProductNotFoundException as e:
            print(e)
        except Exception as e:
            # Likely foreign-key constraint due to existing order_items
            print("Failed to delete product:", e)

    def _add_to_cart(self):
        print("\n-- Add to Cart --")
        cid = _prompt_int("Customer ID: ", min_val=1)
        pid = _prompt_int("Product ID: ", min_val=1)
        qty = _prompt_int("Quantity: ", min_val=1)
        cust = Customer(customer_id=cid)
        prod = Product(product_id=pid)
        try:
            ok = self.repo.addToCart(cust, prod, qty)
            if ok:
                print(f"Added product {pid} (qty {qty}) to cart for customer {cid}.")
        except CustomerNotFoundException as e:
            print(e)
        except ProductNotFoundException as e:
            print(e)
        except ValueError as e:
            print("Invalid input:", e)
        except Exception as e:
            print("Failed to add to cart:", e)

    def _view_cart(self):
        print("\n-- View Cart --")
        cid = _prompt_int("Customer ID: ", min_val=1)
        cust = Customer(customer_id=cid)
        try:
            items: List[Tuple[Product, int]] = self.repo.getAllFromCart(cust)
            if not items:
                print("Cart is empty.")
                return
            _print_line("=")
            print(f"Cart for customer {cid}")
            _print_line("=")
            total = 0.0
            for prod, qty in items:
                line_total = (prod.get_price() or 0.0) * qty
                total += line_total
                print(f"[{prod.get_product_id():>3}] {prod.get_name():<30} "
                      f"₹{prod.get_price():>8.2f}  x {qty:<3} = ₹{line_total:>8.2f}")
            _print_line()
            print(f"Cart Total: ₹{total:.2f}")
        except CustomerNotFoundException as e:
            print(e)
        except Exception as e:
            print("Failed to view cart:", e)

    def _place_order(self):
        print("\n-- Place Order (from current cart) --")
        cid = _prompt_int("Customer ID: ", min_val=1)
        addr = _prompt_nonempty("Shipping Address: ")
        cust = Customer(customer_id=cid)
        try:
            ok = self.repo.placeOrder(cust, None, addr)  # None => use items from cart
            if ok:
                print("Order placed successfully.")
        except CustomerNotFoundException as e:
            print(e)
        except ValueError as e:
            # e.g., empty cart or insufficient stock
            print("Cannot place order:", e)
        except Exception as e:
            print("Failed to place order:", e)

    def _view_customer_orders(self):
        print("\n-- View Customer Orders --")
        cid = _prompt_int("Customer ID: ", min_val=1)
        try:
            rows: List[Dict[str, Any]] = self.repo.getOrdersByCustomer(cid)
            if not rows:
                print("No orders found for this customer.")
                return
            # Group by order_id to present neatly
            grouped: Dict[int, Dict[str, Any]] = {}
            for r in rows:
                oid = r["order_id"]
                if oid not in grouped:
                    grouped[oid] = {"order_date": r["order_date"], "items": []}
                grouped[oid]["items"].append((r["product"], r["quantity"]))

            for oid, data in sorted(grouped.items(), key=lambda kv: kv[1]["order_date"], reverse=True):
                _print_line("=")
                print(f"Order #{oid}  on {data['order_date']}")
                _print_line("-")
                order_total = 0.0
                for prod, qty in data["items"]:
                    line_total = (prod.get_price() or 0.0) * qty
                    order_total += line_total
                    print(f"[{prod.get_product_id():>3}] {prod.get_name():<30} "
                          f"₹{prod.get_price():>8.2f}  x {qty:<3} = ₹{line_total:>8.2f}")
                _print_line()
                print(f"Order Total: ₹{order_total:.2f}")
            _print_line("=")
        except CustomerNotFoundException as e:
            print(e)
        except OrderNotFoundException as e:
            # Not thrown by current implementation for "no orders"; included if your rubric expects it
            print(e)
        except Exception as e:
            print("Failed to view orders:", e)

    # -------- main loop --------

    def run(self):
        while True:
            _print_line("=")
            print("E-COMMERCE APP")
            _print_line("=")
            print("1) Register Customer")
            print("2) Create Product")
            print("3) Delete Product")
            print("4) Add to Cart")
            print("5) View Cart")
            print("6) Place Order")
            print("7) View Customer Order")
            print("0) Exit")
            _print_line()

            choice = input("Choose an option: ").strip()
            if choice == "1":
                self._register_customer()
            elif choice == "2":
                self._create_product()
            elif choice == "3":
                self._delete_product()
            elif choice == "4":
                self._add_to_cart()
            elif choice == "5":
                self._view_cart()
            elif choice == "6":
                self._place_order()
            elif choice == "7":
                self._view_customer_orders()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Run with your Windows-auth config at config/db.properties
    app = EcomApp("config/db.properties")
    app.run()
