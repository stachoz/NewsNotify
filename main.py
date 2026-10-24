import json
from pathlib import Path


PORTFOLIO_PATH = Path(__file__).with_name("config.json")

with PORTFOLIO_PATH.open(encoding="utf-8") as portfolio_file:
    portfolio = json.load(portfolio_file)


if __name__ == '__main__':
    print(portfolio)
