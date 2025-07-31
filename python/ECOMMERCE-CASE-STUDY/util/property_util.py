# # util/property_util.py
# import os

# class DBPropertyUtil:
#     """
#     Reads a .properties file (key=value per line) and returns a pyodbc
#     connection string for SQL Server.

#     Supports BOTH:
#       - Windows Authentication: trusted_connection=yes (no UID/PWD)
#       - SQL Auth: provide user + password (trusted_connection not 'yes')

#     Recognized keys (case-insensitive):
#       driver, server (or host), database, user, password,
#       trusted_connection (yes/no/true/false),
#       encrypt (yes/no), trust_server_certificate (yes/no)
#     """

#     @staticmethod
#     def get_property_string(file_name: str) -> str:
#         if not os.path.isfile(file_name):
#             raise FileNotFoundError(f"Property file not found: {file_name}")

#         props = {}
#         with open(file_name, "r", encoding="utf-8") as f:
#             for line in f:
#                 line = line.strip()
#                 if not line or line.startswith("#"):
#                     continue
#                 if "=" in line:
#                     k, v = line.split("=", 1)
#                     props[k.strip().lower()] = v.strip()

#         # Read properties with sensible defaults
#         driver   = props.get("driver", "ODBC Driver 18 for SQL Server")
#         server   = props.get("server") or props.get("host") or "localhost"
#         database = props.get("database")
#         user     = props.get("user")
#         password = props.get("password")

#         # Flags
#         trusted_conn = (props.get("trusted_connection", "no").lower() in ("yes", "true", "1"))
#         encrypt      = props.get("encrypt", "yes")
#         tsc          = props.get("trust_server_certificate", "yes")

#         if not database:
#             raise ValueError("Missing 'database' in property file.")

#         parts = [f"DRIVER={{{driver}}}".format(driver=driver),
#                  f"SERVER={server}",
#                  f"DATABASE={database}"]

#         # Authentication branch
#         if trusted_conn:
#             parts.append("Trusted_Connection=yes")
#         else:
#             if not user or not password:
#                 raise ValueError("Using SQL authentication requires 'user' and 'password'.")
#             parts.append(f"UID={user}")
#             parts.append(f"PWD={password}")

#         # Security/SSL options (Driver 18 defaults to Encrypt=yes)
#         # Keep explicit so it's clear and configurable.
#         parts.append(f"Encrypt={encrypt}")
#         parts.append(f"TrustServerCertificate={tsc}")

#         return ";".join(parts)
# util/property_util.py
import os

class DBPropertyUtil:
    """
    Reads a .properties file (key=value per line) and returns a pyodbc
    connection string for SQL Server.

    Supports BOTH:
      - Windows Authentication: trusted_connection=yes (no UID/PWD)
      - SQL Auth: provide user + password (trusted_connection not 'yes')

    Recognized keys (case-insensitive):
      driver, server (or host), database, user, password,
      trusted_connection (yes/no/true/false),
      encrypt (yes/no), trust_server_certificate (yes/no)
    """

    @staticmethod
    def get_property_string(file_name: str) -> str:
        if not os.path.isfile(file_name):
            raise FileNotFoundError(f"Property file not found: {file_name}")

        props = {}
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    props[k.strip().lower()] = v.strip()

        # Read properties with sensible defaults
        driver   = props.get("driver", "ODBC Driver 18 for SQL Server")
        server   = props.get("server") or props.get("host") or "localhost"
        database = props.get("database")
        user     = props.get("user")
        password = props.get("password")

        # Flags
        trusted_conn = (props.get("trusted_connection", "no").lower() in ("yes", "true", "1"))
        encrypt      = props.get("encrypt", "yes")
        tsc          = props.get("trust_server_certificate", "yes")

        if not database:
            raise ValueError("Missing 'database' in property file.")

        # Build connection string parts (NOTE: f-strings only; no .format())
        parts = [
            f"DRIVER={{{driver}}}",   # braces are doubled to emit literal {}
            f"SERVER={server}",
            f"DATABASE={database}",
        ]

        if trusted_conn:
            parts.append("Trusted_Connection=yes")
        else:
            if not user or not password:
                raise ValueError("Using SQL authentication requires 'user' and 'password'.")
            parts.append(f"UID={user}")
            parts.append(f"PWD={password}")

        parts.append(f"Encrypt={encrypt}")
        parts.append(f"TrustServerCertificate={tsc}")

        return ";".join(parts)
