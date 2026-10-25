# Weekly Market Research

This is a simple automation for preparing a weekly market research report for the holdings in `config.json`. It uses CoinMarketCap for cryptocurrency prices and Claude with web search to write a short report in polish. The report is saved in `reports/`.

## Requirements

- Python 3.9 or newer
- Python packages listed in `requirements.txt`
- An Anthropic API key, set as `ANTHROPIC_API_KEY`
- A CoinMarketCap API key, set as `CMC_API_KEY`, if you add crypto tickers other than BTC and ETH (those two currently use sample data in `mock_response.py`)

Install the packages with:

```sh
python -m pip install -r requirements.txt
```

Set your Anthropic key in the environment before running. For example, on macOS or Linux:

```sh
export ANTHROPIC_API_KEY="your-key"
```

Set `CMC_API_KEY` the same way if needed. Do not commit API keys to the repository.

## Run

From the project directory, run:

```sh
python main.py
```

Edit `config.json` to change the tracked holdings and base currency. A dated Markdown report will be written to `reports/weekly_report_YYYY-MM-DD.md`.
