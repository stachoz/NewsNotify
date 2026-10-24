import json
from pathlib import Path
import requests
from datetime import datetime, timedelta
from os import getenv
import mock_response
from prompts import build_prompt


API_KEY = getenv("CMC_API_KEY")
PORTFOLIO_PATH = Path(__file__).with_name("config.json")
URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"

headers = {
    "X-CMC_PRO_API_KEY": str(API_KEY)
}

with PORTFOLIO_PATH.open(encoding="utf-8") as portfolio_file:
    portfolio = json.load(portfolio_file)

    symbols = []
    for holding in portfolio["holdings"]:
        if holding.get("type", "").lower() in {"crypto", "cryptocurrency"}:
            symbols.append(holding["ticker"])

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    today_str = today.strftime("%Y-%m-%d")
    seven_days_ago_str = seven_days_ago.strftime("%Y-%m-%d")

    mock_data = {
        "BTC": mock_response.btc_week_json,
        "ETH": mock_response.eth_week_json,
    }
    weekly_data = []

    for symbol in symbols:
        params = {
            "symbol": f"{symbol}",
            "time_start": f"{seven_days_ago_str}",
            "time_end": f"{today_str}",
            "interval": "daily",
            "convert": portfolio.get("base_currency", "USD"),
        }

        if symbol in mock_data:
            weekly_data.append(mock_data[symbol])
        else:
            pass
            # response = requests.get(URL, headers=headers, params=params, timeout=30)
            # response.raise_for_status()
            # weekly_data.append(response.json())


if __name__ == '__main__':
    print(build_prompt(portfolio, weekly_data))
