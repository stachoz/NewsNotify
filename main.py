import json
from pathlib import Path
import requests
from datetime import datetime, timedelta
from os import getenv
import mock_response
from prompts import build_prompt,get_perplexity_prompt
import anthropic

CMC_API_KEY = getenv("CMC_API_KEY")
PORTFOLIO_PATH = Path(__file__).with_name("config.json")
CMC_URL = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/latest"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

def load_weekly_data(config):
    print(f"Loading weekly data for {config}")
    symbols = [
        holding["ticker"]
        for holding in config.get("holdings", [])
        if holding.get("type", "").lower() in {"crypto", "cryptocurrency"}
    ]
    today = datetime.now()
    params_dates = { "time_start": today.strftime("%Y-%m-%d"),
        "time_end": today.strftime("%Y-%m-%d"),
        "interval": "daily",
        "convert": config.get("base_currency", "USD"),
    }
    mock_data = {
        "BTC": mock_response.btc_week_json,
        "ETH": mock_response.eth_week_json,
    }
    weekly_data = []

    for symbol in symbols:
        if symbol in mock_data:
            weekly_data.append(mock_data[symbol])
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
        weekly_data.append(response.json())
    return weekly_data


def run_claude(prompt):
    print("run prompt")
    client = anthropic.Anthropic()

    MODEL = "claude-sonnet-5-5"     # or "claude-haiku-5-5"
    TOOLS = [{
        "type": "web_search_20260318",
        "name": "web_search",
        "max_uses": 25,                  # hard cap on searches per request = cost control
        "allowed_callers": ["direct"],   # lets Claude call search directly
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
    data_witH_prices = load_weekly_data(config)
    prompt = get_perplexity_prompt(config, data_witH_prices)
    print(prompt)
    print("\n")
    # print(run_claude(prompt))
