import os
import datetime
import time
import json
import re
import database
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge

def get_json(response_str):
    """Safely loads a JSON string, returning a dict."""
    try:
        return json.loads(response_str)
    except (json.JSONDecodeError, TypeError):
        return {}

def fetch_and_store_data():
    """Fetches Nifty 50 options data from Samco API and stores it."""
    try:
        user_id = os.environ.get('SAMCO_USER_ID')
        password = os.environ.get('SAMCO_PASSWORD')
        yob = os.environ.get('SAMCO_YOB')

        if not all([user_id, password, yob]):
            print("Error: Missing Samco credentials.")
            return

        samco = StocknoteAPIPythonBridge()
        login_data = get_json(samco.login(body={"userId": user_id, "password": password, "yob": yob}))

        if login_data.get('status') != 'Success':
            print("Samco login failed:", login_data.get('statusMessage'))
            return

        samco.set_session_token(sessionToken=login_data.get('sessionToken'))
        print("Samco login successful.")

        index_quote_res = samco.index_quote(indexName='NIFTY 50')
        index_quote_data = get_json(index_quote_res)

        if not index_quote_data.get('indexDetails'):
            print("Could not fetch Nifty 50 spot price.")
            return
        spot_price = float(index_quote_data['indexDetails'][0]['spotPrice'])

        atm_strike = round(spot_price / 50) * 50
        strikes = [atm_strike + i * 50 for i in range(-10, 11)]

        search_res = samco.search_equity_derivative(search_symbol_name='NIFTY', exchange='NFO')
        search_data = get_json(search_res)

        if not search_data.get('searchResults'):
            print("Could not find a Nifty derivative to get expiry date.")
            return

        first_symbol = search_data['searchResults'][0].get('tradingSymbol')
        if not first_symbol:
            print("Could not get a trading symbol from search results.")
            return

        match = re.search(r'NIFTY(\d{2}[A-Z]{3}\d{2})', first_symbol)
        if not match:
            print(f"Could not parse expiry date from symbol: {first_symbol}")
            return

        expiry_date_str = match.group(1)
        expiry_date = datetime.datetime.strptime(expiry_date_str, '%d%b%y').strftime('%Y-%m-%d')
        print(f"Using expiry date: {expiry_date}")

        records_to_insert = []
        now_timestamp = datetime.datetime.now()

        for strike in strikes:
            option_res = samco.get_option_chain(
                search_symbol_name='Nifty',
                exchange='NFO',
                expiry_date=expiry_date,
                strike_price=str(strike)
            )
            option_data = get_json(option_res)

            if option_data.get('optionChainDetails'):
                for item in option_data['optionChainDetails']:
                    volume = int(item.get('volume', 0))
                    opt_type = item.get('optionType')
                    if opt_type in ['CE', 'PE']:
                        records_to_insert.append((now_timestamp, strike, opt_type, volume))

            time.sleep(0.3)

        if records_to_insert:
            database.insert_option_data(records_to_insert)
            print(f"Successfully fetched and stored {len(records_to_insert)} records.")
        else:
            print("No option data found for the specified strikes.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    database.init_db()
    fetch_and_store_data()

    latest_data = database.get_latest_data()
    if latest_data:
        print("\nLatest data from DB:")
        for row in latest_data:
            print(row)
