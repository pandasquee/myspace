"""
Database connection and query utilities.
"""
import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

# Initialize connection pool
_pool = SimpleConnectionPool(
    1, 20,
    os.environ.get('DATABASE_URL')
)

@contextmanager
def get_db_connection():
    """Get a database connection from the pool."""
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)

def close_all_connections():
    """Close all database connections in the pool."""
    if _pool:
        _pool.closeall()
