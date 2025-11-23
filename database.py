import mysql.connector
from config import Config

def get_connection():
    """Create and return a database connection."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASS,
        database=Config.DB_NAME,
        autocommit=True
    )

def query_all(query, params=None):
    """Execute a SELECT query and return all results."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def query_one(query, params=None):
    """Execute a SELECT query and return one result."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def execute_query(query, params=None):
    """Execute an INSERT/UPDATE/DELETE query and return last inserted ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id