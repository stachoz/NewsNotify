import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import anthropic
import requests

from email_notification import send_report
from prompts import get_weekly_prompt

PORTFOLIO_PATH = Path(__file__).with_name("config.json")
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"
REPORTS_PATH = Path(__file__).with_name("reports")

CLAUDE_MODEL = "claude-haiku-5-5"
CLAUDE_TOOLS = [
    {
        "type": "web_search_20260318",
        "name": "web_search",
        "max_uses": 25,
        "allowed_callers": ["direct"],
        "user_location": {
            "type": "approximate",
            "country": "PL",
            "timezone": "Europe/Warsaw",
        },
    }
]


def _fetch_symbol_data(symbol: str, params: dict[str, str]) -> dict[str, Any]:
    api_key = os.getenv("CMC_API_KEY")
    if not api_key:
        raise RuntimeError(f"CMC_API_KEY is required to fetch prices for {symbol}.")

    response = requests.get(
        CMC_URL,
        headers={"X-CMC_PRO_API_KEY": api_key},
        params={"symbol": symbol, **params},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _extract_latest_quote(response_data: dict[str, Any]) -> dict[str, Any]:
    latest_quote = response_data["data"]["quotes"][-1]["quote"]["USD"]
    return {
        "price": latest_quote["price"],
        "percent_change_7d": latest_quote["percent_change_7d"],
        "timestamp": latest_quote["timestamp"],
    }


def load_weekly_data(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Fetch the latest weekly quote data for crypto holdings in the config."""
    symbols = [
        holding["ticker"]
        for holding in config.get("holdings", [])
        if holding.get("type", "").lower() in {"crypto", "cryptocurrency"}
    ]

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    params = {
        "time_start": seven_days_ago.strftime("%Y-%m-%d"),
        "time_end": today.strftime("%Y-%m-%d"),
        "interval": "daily",
        "convert": config.get("base_currency", "USD"),
    }

    print(f"Loading weekly data for {len(symbols)} crypto holdings")
    return {
        response_data["data"]["symbol"]: _extract_latest_quote(response_data)
        for response_data in (_fetch_symbol_data(symbol, params) for symbol in symbols)
    }


def _get_claude_response(client: anthropic.Anthropic, prompt: str) -> Any:
    """Continue Claude's response if it pauses before completing the turn."""
    messages = [{"role": "user", "content": prompt}]

    while True:
        with client.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=128000,
            messages=messages,
            tools=CLAUDE_TOOLS,
        ) as stream:
            response = stream.get_final_message()

        if response.stop_reason != "pause_turn":
            return response

        messages.append({"role": "assistant", "content": response.content})


def run_claude(prompt: str) -> str:
    print("Generating report with Claude")
    client = anthropic.Anthropic()
    response = _get_claude_response(client, prompt)

    report = "".join(block.text for block in response.content if block.type == "text")
    usage = response.usage
    print(f"Input tokens: {usage.input_tokens} | output tokens: {usage.output_tokens}")
    print(f"Searches billed: {usage.server_tool_use.web_search_requests}")
    return report


def load_config(file_path: Path) -> dict[str, Any]:
    with file_path.open(encoding="utf-8") as config_file:
        return json.load(config_file)


def save_report(report: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"weekly_report_{datetime.now():%Y-%m-%d}.md"
    report_path.write_text(report.rstrip() + "\n", encoding="utf-8")
    print(f"Report saved to {report_path}")
    return report_path


def main() -> None:
    config = load_config(PORTFOLIO_PATH)
    crypto_data = load_weekly_data(config)
    prompt = get_weekly_prompt(config, crypto_data)
    report = run_claude(prompt)
    report_path = save_report(report, REPORTS_PATH)
    receiver_email = os.getenv("GMAIL_EMAIL", "")
    send_report(report_path, receiver_email)


if __name__ == "__main__":
    main()
