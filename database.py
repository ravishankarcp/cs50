import sqlite3
import datetime

DB_NAME = "options_data.db"

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS option_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            strike_price INTEGER NOT NULL,
            option_type TEXT NOT NULL,
            volume INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_option_data(data):
    """Inserts a list of option data tuples into the database.

    Args:
        data (list): A list of tuples, where each tuple is
                     (timestamp, strike_price, option_type, volume)
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO option_data (timestamp, strike_price, option_type, volume)
        VALUES (?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def get_latest_data():
    """Retrieves the latest set of option data from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Find the latest timestamp
    cursor.execute("SELECT MAX(timestamp) FROM option_data")
    latest_timestamp = cursor.fetchone()[0]

    if not latest_timestamp:
        return []

    # Get all data with the latest timestamp
    cursor.execute("""
        SELECT strike_price, option_type, volume
        FROM option_data
        WHERE timestamp = ?
        ORDER BY strike_price
    """, (latest_timestamp,))

    data = cursor.fetchall()
    conn.close()
    return data

if __name__ == '__main__':
    # For testing purposes
    print("Initializing the database...")
    init_db()
    print("Database initialized.")

    # Example usage:
    # now = datetime.datetime.now()
    # sample_data = [
    #     (now, 22000, 'CE', 150000),
    #     (now, 22000, 'PE', 120000),
    #     (now, 22100, 'CE', 100000),
    #     (now, 22100, 'PE', 110000),
    # ]
    # insert_option_data(sample_data)
    # print("Sample data inserted.")
    #
    # latest_data = get_latest_data()
    # print("Latest data retrieved:")
    # for row in latest_data:
    #     print(row)
