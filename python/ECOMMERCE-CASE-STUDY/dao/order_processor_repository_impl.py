# dao/order_processor_repository_impl.py
from typing import List, Tuple, Optional, Dict, Any
import pyodbc

from dao.order_processor_repository import OrderProcessorRepository
from entity.product import Product
from entity.customer import Customer
from myexceptions import (
    CustomerNotFoundException,
    ProductNotFoundException,
    OrderNotFoundException,
)
from util.db_connection import DBConnection


class OrderProcessorRepositoryImpl(OrderProcessorRepository):
    """
    Concrete implementation for all repository methods.
    Uses pyodbc connection from util.DBConnection.
    """

    def __init__(self, prop_file: str = "config/db.properties"):
        # One shared connection for this repo
        self.conn = DBConnection.get_connection(prop_file)

    # ---------- helpers ----------

    def _ensure_customer_exists(self, customer_id: int) -> None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM dbo.customers WHERE customer_id = ?", customer_id)
            if cur.fetchone() is None:
                raise CustomerNotFoundException(customer_id)

    def _ensure_product_exists(self, product_id: int) -> None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM dbo.products WHERE product_id = ?", product_id)
            if cur.fetchone() is None:
                raise ProductNotFoundException(product_id)

    def _load_product(self, product_id: int) -> Product:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT product_id, name, price, [description], stockQuantity "
                "FROM dbo.products WHERE product_id = ?",
                product_id,
            )
            row = cur.fetchone()
            if row is None:
                raise ProductNotFoundException(product_id)
            return Product(
                product_id=row[0],
                name=row[1],
                price=float(row[2]),
                description=row[3],
                stockQuantity=int(row[4]),
            )

    def createProduct(self, product: Product) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dbo.products (name, price, [description], stockQuantity)
                OUTPUT INSERTED.product_id
                VALUES (?, ?, ?, ?)
                """,
                product.get_name(),
                product.get_price(),
                product.get_description(),
                product.get_stockQuantity(),
            )
            row = cur.fetchone()
            if not row or row[0] is None:
                self.conn.rollback()
                raise RuntimeError("Failed to obtain new product_id after insert.")
            product.set_product_id(int(row[0]))
        self.conn.commit()
        return True

    def createCustomer(self, customer: Customer) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dbo.customers (name, email, [password])
                OUTPUT INSERTED.customer_id
                VALUES (?, ?, ?)
                """,
                customer.get_name(),
                customer.get_email(),
                customer.get_password(),
            )
            row = cur.fetchone()         # e.g., (42,)
            if not row or row[0] is None:
                self.conn.rollback()
                raise RuntimeError("Failed to obtain new customer_id after insert.")
            customer.set_customer_id(int(row[0]))
        self.conn.commit()
        return True


    def deleteProduct(self, productId: int) -> bool:
        
        self._ensure_product_exists(productId)
        with self.conn.cursor() as cur:
            # clean cart rows referencing this product to avoid FK issues
            cur.execute("DELETE FROM dbo.cart WHERE product_id = ?", productId)
            
            try:
                cur.execute("DELETE FROM dbo.products WHERE product_id = ?", productId)
            except pyodbc.IntegrityError:
                # Likely referenced by order_items
                self.conn.rollback()
                raise
        self.conn.commit()
        return True

    def deleteCustomer(self, customerId: int) -> bool:
        # ensure customer exists first
        self._ensure_customer_exists(customerId)
        with self.conn.cursor() as cur:
            # remove from cart; orders may still reference the customer (FK prevents delete)
            cur.execute("DELETE FROM dbo.cart WHERE customer_id = ?", customerId)
            try:
                cur.execute("DELETE FROM dbo.customers WHERE customer_id = ?", customerId)
            except pyodbc.IntegrityError:
                # Customer has orders; deletion not allowed due to FK in orders
                self.conn.rollback()
                raise
        self.conn.commit()
        return True

    # ---------- cart ----------

    def addToCart(self, customer: Customer, product: Product, quantity: int) -> bool:
        if quantity <= 0:
            raise ValueError("quantity must be > 0")

        customer_id = customer.get_customer_id()
        product_id = product.get_product_id()

        self._ensure_customer_exists(customer_id)
        self._ensure_product_exists(product_id)

        with self.conn.cursor() as cur:
            # upsert-like behavior: if exists, increase quantity; else insert
            cur.execute(
                "SELECT quantity FROM dbo.cart WHERE customer_id = ? AND product_id = ?",
                customer_id,
                product_id,
            )
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "INSERT INTO dbo.cart (customer_id, product_id, quantity) VALUES (?, ?, ?)",
                    customer_id,
                    product_id,
                    quantity,
                )
            else:
                cur.execute(
                    "UPDATE dbo.cart SET quantity = quantity + ? WHERE customer_id = ? AND product_id = ?",
                    quantity,
                    customer_id,
                    product_id,
                )
        self.conn.commit()
        return True

    def removeFromCart(self, customer: Customer, product: Product) -> bool:
        customer_id = customer.get_customer_id()
        product_id = product.get_product_id()

        self._ensure_customer_exists(customer_id)
        self._ensure_product_exists(product_id)

        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM dbo.cart WHERE customer_id = ? AND product_id = ?",
                customer_id,
                product_id,
            )
            removed = cur.rowcount > 0
        self.conn.commit()
        return removed

    def getAllFromCart(self, customer: Customer) -> List[Tuple[Product, int]]:
        customer_id = customer.get_customer_id()
        self._ensure_customer_exists(customer_id)

        items: List[Tuple[Product, int]] = []
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.product_id, p.name, p.price, p.[description], p.stockQuantity, c.quantity
                FROM dbo.cart c
                JOIN dbo.products p ON p.product_id = c.product_id
                WHERE c.customer_id = ?
                ORDER BY p.name
                """,
                customer_id,
            )
            for row in cur.fetchall():
                prod = Product(
                    product_id=int(row[0]),
                    name=row[1],
                    price=float(row[2]),
                    description=row[3],
                    stockQuantity=int(row[4]),
                )
                qty = int(row[5])
                items.append((prod, qty))
        return items

    # ---------- orders ----------

    def placeOrder(
        self,
        customer: Customer,
        items: Optional[List[Tuple[Product, int]]],
        shippingAddress: str,
    ) -> bool:
        """
        If items is None, takes the current cart items for the customer.
        Validates stock, creates an order, inserts order_items, decrements stock,
        and clears the purchased items from the cart.
        """
        customer_id = customer.get_customer_id()
        self._ensure_customer_exists(customer_id)

        # Determine source items
        if items is None:
            cart_items = self.getAllFromCart(customer)
            if not cart_items:
                raise ValueError("Cart is empty; nothing to order.")
            items = cart_items

        # Build a snapshot {product_id: (Product, qty)} and validate products/qty
        prod_map: Dict[int, Tuple[Product, int]] = {}
        for prod, qty in items:
            if qty <= 0:
                raise ValueError(f"Invalid quantity {qty} for product_id={prod.get_product_id()}")
            # Ensure product still exists & load latest stock/pricing
            p = self._load_product(prod.get_product_id())
            prod_map[p.get_product_id()] = (p, qty)

        # Validate stock and compute total
        total = 0.0
        for p, qty in prod_map.values():
            if p.get_stockQuantity() < qty:
                raise ValueError(f"Insufficient stock for '{p.get_name()}': have {p.get_stockQuantity()}, need {qty}")
            total += (p.get_price() or 0.0) * qty

        # Transaction: create order, insert items, decrement stock, clear cart
        try:
            with self.conn.cursor() as cur:
                # 1) create order
                cur.execute(
                    """
                    INSERT INTO dbo.orders (customer_id, total_price, shipping_address)
                    OUTPUT INSERTED.order_id
                    VALUES (?, ?, ?)
                    """,
                    customer_id, total, shippingAddress,
                )
                row = cur.fetchone()
                if not row or row[0] is None:
                    raise RuntimeError("Failed to obtain new order_id after insert.")
                order_id = int(row[0])


                # 2) insert order_items + 3) decrement stock
                for p, qty in prod_map.values():
                    cur.execute(
                        "INSERT INTO dbo.order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                        order_id,
                        p.get_product_id(),
                        qty,
                    )
                    cur.execute(
                        "UPDATE dbo.products SET stockQuantity = stockQuantity - ? WHERE product_id = ?",
                        qty,
                        p.get_product_id(),
                    )

                # 4) clear purchased items from cart (for this customer)
                for pid in prod_map.keys():
                    cur.execute(
                        "DELETE FROM dbo.cart WHERE customer_id = ? AND product_id = ?",
                        customer_id,
                        pid,
                    )

            self.conn.commit()
            return True

        except Exception:
            self.conn.rollback()
            raise

    def getOrdersByCustomer(self, customerId: int) -> List[Dict[str, Any]]:
        """
        Returns a list of dicts:
          { 'order_id': int, 'order_date': datetime, 'product': Product, 'quantity': int }
        for all orders belonging to the given customer.
        """
        self._ensure_customer_exists(customerId)

        results: List[Dict[str, Any]] = []
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    o.order_id, o.order_date,
                    p.product_id, p.name, p.price, p.[description], p.stockQuantity,
                    oi.quantity
                FROM dbo.orders o
                JOIN dbo.order_items oi ON oi.order_id = o.order_id
                JOIN dbo.products p ON p.product_id = oi.product_id
                WHERE o.customer_id = ?
                ORDER BY o.order_date DESC, o.order_id DESC
                """,
                customerId,
            )
            rows = cur.fetchall()

        if not rows:
            # No orders found for a valid customer is not an error per se; return empty list.
            return results

        for r in rows:
            prod = Product(
                product_id=int(r[2]),
                name=r[3],
                price=float(r[4]),
                description=r[5],
                stockQuantity=int(r[6]),
            )
            results.append(
                {
                    "order_id": int(r[0]),
                    "order_date": r[1],
                    "product": prod,
                    "quantity": int(r[7]),
                }
            )
        return results
