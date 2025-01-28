import psycopg2
from psycopg2 import pool

class Database:
    _connection_pool = None

    @staticmethod
    def initialize(host, database, user, password, port=5432):
        """Initialize the connection pool."""
        Database._connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20, host=host, database=database, user=user, password=password, port=port
        )

    @staticmethod
    def get_connection():
        """Get a connection from the pool."""
        if Database._connection_pool is None:
            raise Exception("Database connection pool is not initialized.")
        return Database._connection_pool.getconn()

    @staticmethod
    def release_connection(connection):
        """Release a connection back to the pool."""
        if Database._connection_pool is None:
            raise Exception("Database connection pool is not initialized.")
        Database._connection_pool.putconn(connection)

    @staticmethod
    def close_all_connections():
        """Close all connections in the pool."""
        if Database._connection_pool is not None:
            Database._connection_pool.closeall()
