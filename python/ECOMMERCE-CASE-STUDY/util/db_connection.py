# util/db_connection.py
import threading
import pyodbc
from typing import Optional
from util.property_util import DBPropertyUtil
from util.db_conn_util import DBConnUtil

class DBConnection:
    """
    Singleton-style provider to get one shared connection.
    Call DBConnection.get_connection("config/db.properties")
    """
    _lock = threading.Lock()
    _conn: Optional[pyodbc.Connection] = None
    _last_prop_file: Optional[str] = None

    @staticmethod
    def get_connection(prop_file: str = "config/db.properties") -> pyodbc.Connection:
        if DBConnection._conn is None or DBConnection._last_prop_file != prop_file:
            with DBConnection._lock:
                if DBConnection._conn is None or DBConnection._last_prop_file != prop_file:
                    conn_str = DBPropertyUtil.get_property_string(prop_file)
                    DBConnection._conn = DBConnUtil.get_connection(conn_str)
                    DBConnection._last_prop_file = prop_file
        return DBConnection._conn
