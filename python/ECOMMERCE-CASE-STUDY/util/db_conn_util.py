# util/db_conn_util.py
import pyodbc
from typing import Optional

class DBConnUtil:
    """
    Returns a live pyodbc connection given a connection string.
    """

    @staticmethod
    def get_connection(conn_str: Optional[str]) -> pyodbc.Connection:
        if not conn_str or not conn_str.strip():
            raise ValueError("A valid connection string is required.")
        # autocommit=False so DAO methods can control transactions explicitly
        return pyodbc.connect(conn_str, autocommit=False)
