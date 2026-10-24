import json
from pathlib import Path
import requests
from datetime import datetime, timedelta
from os import getenv
import mock_response


API_KEY = getenv("CMC_API_KEY")
PORTFOLIO_PATH = Path(__file__).with_name("config.json")
URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"

headers = {
    "X-CMC_PRO_API_KEY": str(API_KEY)
}

with PORTFOLIO_PATH.open(encoding="utf-8") as portfolio_file:
    portfolio = json.load(portfolio_file)

    symbols = []
    for ticker in portfolio["holdings"]:
        symbols.append(ticker["ticker"])

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    today_str = today.strftime("%Y-%m-%d")
    seven_days_ago_str = seven_days_ago.strftime("%Y-%m-%d")

    weekly_data = [mock_response.btc_week_json, mock_response.eth_week_json]

    for symbol in symbols:
        params = {
            "symbol": f"{symbol}",
            "time_start": f"{seven_days_ago_str}",
            "time_end": f"{today_str}",
            "interval": "daily",
            "convert": "USD",
        }

        # response = requests.get(
        #     URL, headers=headers, params=params, timeout=30
        # )
        # response.raise_for_status()
        # weekly_data.append(response.json())


    for coin_week_data in weekly_data:
        quotes = coin_week_data["data"]["quotes"]
        print(quotes)

if __name__ == '__main__':
    pass
