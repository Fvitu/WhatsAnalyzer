import os
import pymysql
from pymysql.cursors import DictCursor
import threading
import time
import logging
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("database.log"), logging.StreamHandler()],
)
logger = logging.getLogger("db_manager")


class DatabaseManager:
    """Database connection manager with connection pooling and auto-reconnect capabilities"""

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one instance of DatabaseManager exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize database connection parameters"""
        settings = self._load_settings()
        self.host = settings["host"]
        self.user = settings["user"]
        self.port = settings["port"]
        self.password = settings["password"]
        self.database = settings["database"]
        self.ssl = settings.get("ssl")
        self.pool = []
        self.max_pool_size = settings.get("max_pool_size", 10)
        self.connection_timeout = settings.get("connection_timeout", 300)
        self.last_checked = time.time()
        self.check_interval = settings.get("check_interval", 60)

    def get_connection(self):
        """Get a connection from the pool or create a new one if none is available"""
        # Check and clean pool periodically
        current_time = time.time()
        if current_time - self.last_checked > self.check_interval:
            self._clean_pool()
            self.last_checked = current_time

        # Try to get a connection from the pool
        if self.pool:
            connection = self.pool.pop()
            try:
                # Test if connection is still alive
                connection.ping(reconnect=True)
                return connection
            except Exception as e:
                logger.warning(f"Stale connection in pool: {e}")
                # If connection is stale, create a new one
                return self._create_new_connection()
        else:
            # Create a new connection if pool is empty
            return self._create_new_connection()

    def _create_new_connection(self):
        """Create a new database connection"""
        try:
            connect_kwargs = {
                "host": self.host,
                "user": self.user,
                "port": self.port,
                "password": self.password,
                "database": self.database,
                "cursorclass": DictCursor,
                "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", 10)),
                "autocommit": False,
                "charset": "utf8mb4",
            }

            if self.ssl:
                connect_kwargs["ssl"] = self.ssl

            connection = pymysql.connect(**connect_kwargs)
            logger.info("Created new database connection")
            return connection
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise

    def return_connection(self, connection):
        """Return a connection to the pool"""
        if connection:
            # Only return the connection to the pool if we haven't reached max size
            if len(self.pool) < self.max_pool_size:
                try:
                    # Make sure we commit any pending transactions
                    connection.commit()
                    self.pool.append(connection)
                except:
                    # If there's an issue with the connection, don't add it back to the pool
                    try:
                        connection.close()
                    except:
                        pass
            else:
                # Close the connection if pool is full
                try:
                    connection.close()
                except:
                    pass

    def _clean_pool(self):
        """Clean up idle connections in the pool"""
        now = time.time()
        active_connections = []

        for conn in self.pool:
            try:
                # Test if connection is still good
                conn.ping(reconnect=False)
                active_connections.append(conn)
            except:
                # If connection is bad, close it
                try:
                    conn.close()
                except:
                    pass

        self.pool = active_connections
        logger.info(f"Cleaned connection pool. Current size: {len(self.pool)}")

    def execute_query(self, query, params=None, commit=True):
        """Execute a query and return results"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)

            if commit:
                conn.commit()

            if query.strip().upper().startswith(("SELECT", "SHOW")):
                result = cursor.fetchall()
                return result
            else:
                return cursor.rowcount

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database query error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)

    def execute_many(self, query, params_list, commit=True):
        """Execute a query with multiple parameter sets"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)

            if commit:
                conn.commit()

            return cursor.rowcount

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database executemany error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)

    def close_all(self):
        """Close all connections in the pool"""
        for connection in self.pool:
            try:
                connection.close()
            except:
                pass
        self.pool = []

    def _load_settings(self) -> Dict[str, Any]:
        """Load database settings from environment variables or DATABASE_URL."""
        url = os.getenv("DATABASE_URL")
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in {"mysql", "mysql+pymysql"}:
                raise ValueError(
                    "Unsupported database scheme. Use mysql or mysql+pymysql."
                )
            query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            ssl_config = self._build_ssl_config(query_params)
            return {
                "host": parsed.hostname or "localhost",
                "user": parsed.username or "",
                "port": parsed.port or 3306,
                "password": parsed.password or "",
                "database": parsed.path.lstrip("/") or os.getenv("DB_NAME", ""),
                "ssl": ssl_config,
                "max_pool_size": int(
                    os.getenv("DB_MAX_POOL_SIZE", query_params.get("max_pool_size", 10))
                ),
                "connection_timeout": int(
                    os.getenv(
                        "DB_CONNECTION_TIMEOUT",
                        query_params.get("connection_timeout", 300),
                    )
                ),
                "check_interval": int(
                    os.getenv(
                        "DB_CHECK_INTERVAL", query_params.get("check_interval", 60)
                    )
                ),
            }

        ssl_config = self._build_ssl_config()
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", ""),
            "port": int(os.getenv("DB_PORT", 3306)),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", ""),
            "ssl": ssl_config,
            "max_pool_size": int(os.getenv("DB_MAX_POOL_SIZE", 10)),
            "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", 300)),
            "check_interval": int(os.getenv("DB_CHECK_INTERVAL", 60)),
        }

    def _build_ssl_config(
        self, query_params: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        params = query_params or {}
        ssl_mode = os.getenv("DB_SSL_MODE", params.get("sslmode", "")).lower()
        ssl_ca = os.getenv("DB_SSL_CA", params.get("ssl_ca", ""))
        ssl_cert = os.getenv("DB_SSL_CERT", params.get("ssl_cert", ""))
        ssl_key = os.getenv("DB_SSL_KEY", params.get("ssl_key", ""))

        if ssl_mode in {"require", "verify_ca", "verify_identity"} or any(
            [ssl_ca, ssl_cert, ssl_key]
        ):
            ssl_config: Dict[str, Any] = {}
            if ssl_ca:
                ssl_config["ca"] = ssl_ca
            if ssl_cert:
                ssl_config["cert"] = ssl_cert
            if ssl_key:
                ssl_config["key"] = ssl_key
            if ssl_mode == "verify_identity":
                ssl_config["check_hostname"] = True
            return ssl_config or None
        return None
