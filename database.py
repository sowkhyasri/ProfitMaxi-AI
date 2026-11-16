
import sqlite3
import os

DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "profitmaxi.db"
)


def get_connection():
    """Create and return a database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS upload_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_records INTEGER,
            total_revenue REAL,
            total_profit REAL
        )
    """)

    connection.commit()
    connection.close()


def save_upload(filename, total_records, total_revenue, total_profit):
    """Save uploaded dataset analysis summary."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO upload_history (
            filename,
            total_records,
            total_revenue,
            total_profit
        )
        VALUES (?, ?, ?, ?)
    """, (
        filename,
        total_records,
        total_revenue,
        total_profit
    ))

    connection.commit()
    connection.close()


def get_upload_history():
    """Retrieve previous upload summaries."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM upload_history
        ORDER BY upload_date DESC
    """)

    records = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return records


initialize_database()
