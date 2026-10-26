import json
import os
from pathlib import Path
import requests
from datetime import datetime, timedelta
from os import getenv
import mock_response
from prompts import get_prompt
import anthropic
from email_notification import send_report

CMC_API_KEY = getenv("CMC_API_KEY")
PORTFOLIO_PATH = Path(__file__).with_name("config.json")
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
REPORTS_PATH = Path(__file__).with_name("reports")

def load_weekly_data(config):
    print(f"Loading weekly data for {config}")
    symbols = [
        holding["ticker"]
        for holding in config.get("holdings", [])
        if holding.get("type", "").lower() in {"crypto", "cryptocurrency"}
    ]
    today = datetime.now()
    seven_days_ago = today - timedelta(days = 7)
    params_dates = {
        "time_start": seven_days_ago.strftime("%Y-%m-%d"),
        "time_end": today.strftime("%Y-%m-%d"),
        "interval": "daily",
        "convert": config.get("base_currency", "USD"),
    }
    mock_data = {
        "BTC": mock_response.btc_week_json,
        "ETH": mock_response.eth_week_json,
    }
    weekly_data_dirty = []

    for symbol in symbols:
        if symbol in mock_data:
            weekly_data_dirty.append(mock_data[symbol])
            continue
        if not CMC_API_KEY:
            raise RuntimeError(f"CMC_API_KEY is required to fetch prices for {symbol}.")
        response = requests.get(
            CMC_URL,
            headers={"X-CMC_PRO_API_KEY": CMC_API_KEY},
            params={"symbol": symbol, **params_dates},
            timeout=30,
        )
        response.raise_for_status()
        weekly_data_dirty.append(response.json())

    clean_weekly_data = {}
    for coin_dirty_data in weekly_data_dirty:
        name = coin_dirty_data["data"]["symbol"]
        last_quote = coin_dirty_data["data"]["quotes"][-1]["quote"]["USD"]
        clean_weekly_data[name] = {
            "price": last_quote["price"],
            "percent_change_7d": last_quote["percent_change_7d"],
            "timestamp": last_quote["timestamp"],
        }

    return clean_weekly_data


def run_claude(prompt):
    print("run prompt")
    client = anthropic.Anthropic()

    MODEL = "claude-haiku-5-5"
    TOOLS = [{
        "type": "web_search_20260318",
        "name": "web_search",
        "max_uses": 25,
        "allowed_callers": ["direct"],
        "user_location": {"type": "approximate", "country": "PL", "timezone": "Europe/Warsaw"},
    }]

    messages = [{"role": "user", "content": prompt}]

    while True:
        with client.messages.stream(
                model=MODEL, max_tokens=128000, messages=messages, tools=TOOLS
        ) as stream:
            response = stream.get_final_message()
        if response.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": response.content})

    report = "".join(b.text for b in response.content if b.type == "text")

    usage = response.usage
    print("Input tokens:", usage.input_tokens, "| output tokens:", usage.output_tokens)
    print("Searches billed:", usage.server_tool_use.web_search_requests)
    return report


if __name__ == '__main__':
    with PORTFOLIO_PATH.open(encoding="utf-8") as portfolio_file:
        config = json.load(portfolio_file)
    crypto_data = load_weekly_data(config)
    prompt = get_prompt(config, crypto_data)
    report = run_claude(prompt)
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_PATH / f"weekly_report_{datetime.now():%Y-%m-%d}.md"
    report_path.write_text(report.rstrip() + "\n", encoding="utf-8")
    print(f"Report saved to {report_path}")
    send_report(Path("reports/weekly_report_2026-10-25.md"), str(os.getenv("GMAIL_EMAIL")))
