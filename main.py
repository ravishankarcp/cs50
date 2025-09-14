import threading
import time
import data_fetcher
from app import app
import database

def run_data_fetcher():
    """Runs the data fetcher every 60 seconds."""
    while True:
        print("Fetching new data...")
        data_fetcher.fetch_and_store_data()
        print("Data fetch complete. Waiting for 60 seconds.")
        time.sleep(60)

if __name__ == '__main__':
    # Initialize the database
    database.init_db()

    # Run the data fetcher in a background thread
    fetcher_thread = threading.Thread(target=run_data_fetcher, daemon=True)
    fetcher_thread.start()

    # Start the Flask app
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=8080)
