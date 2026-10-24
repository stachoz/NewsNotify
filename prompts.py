from datetime import date, timedelta

def _format_number(value, currency):
    if value is None:
        return "brak danych"
    return f"{float(value):,.2f} {currency}".replace(",", " ").replace(".", ",")


def _crypto_details(holding, data, currency):
    quotes = data.get("data", {}).get("quotes", [])
    start_price = end_price = None
    if quotes:
        start_price = quotes[0].get("quote", {}).get(currency, {}).get("price")
        end_price = quotes[-1].get("quote", {}).get(currency, {}).get("price")
    change = "brak danych"
    if start_price not in (None, 0) and end_price is not None:
        change = f"{(float(end_price) - float(start_price)) / float(start_price) * 100:+.2f}%".replace(".", ",")
    name = data.get("data", {}).get("name", holding["ticker"])
    return f"- {name} ({holding['ticker']}): cena początkowa {_format_number(start_price, currency)}, cena końcowa {_format_number(end_price, currency)}, zmiana {change}."


def build_prompt(config, weekly_data=None):
    weekly_data = weekly_data or []
    by_symbol = {
        item.get("data", {}).get("symbol"): item
        for item in weekly_data
        if item.get("data", {}).get("symbol")
    }
    currency = config.get("base_currency", "USD")
    holdings = config.get("holdings", [])
    crypto_holdings = [h for h in holdings if h.get("type", "").lower() in {"crypto", "cryptocurrency"}]
    other_holdings = [h for h in holdings if h not in crypto_holdings]
    crypto_lines = [_crypto_details(h, by_symbol.get(h["ticker"], {}), currency) for h in crypto_holdings]
    watch_items = [str(item) for item in config.get("market_watch", [])]
    other_lines = [f"- {h.get('ticker', 'Nieznany instrument')} (typ: {h.get('type', 'nie podano')})" for h in other_holdings]
    other_lines.extend(f"- {item}" for item in watch_items)
    today = date.today()
    date_from, date_to = today - timedelta(days=7), today
    next_from, next_to = today + timedelta(days=1), today + timedelta(days=7)
    banks = config.get("central_banks", "Fed, EBC, NBP")
    local_currency = config.get("local_currency", "PLN")
    crypto_block = "\n".join(crypto_lines) or "- Brak kryptowalut w konfiguracji."
    instruments_block = "\n".join(other_lines) or "- Brak pozostałych instrumentów w konfiguracji."
    extra_topics = config.get("extra_topics", "")
    extra_topics_block = f"\n- Dodatkowe tematy: {extra_topics}" if extra_topics else ""
    poland_yield = ", Polska" if "NBP" in banks else ""

    return f"""Jesteś asystentem przygotowującym tygodniowy przegląd informacji rynkowych dla prywatnego inwestora. Pisz po polsku, rzeczowo i zwięźle.

DZISIEJSZA DATA: {today:%Y-%m-%d}
OKRES PRZEGLĄDU: {date_from:%Y-%m-%d} – {date_to:%Y-%m-%d}
OKRES KALENDARZA: {next_from:%Y-%m-%d} – {next_to:%Y-%m-%d}

ZASADY
1. Korzystaj z wyszukiwarki internetowej. Uwzględniaj informacje opublikowane w okresie przeglądu i sprawdzaj datę publikacji.
2. Każdą informację opatrz źródłem, linkiem URL i datą publikacji. Preferuj źródła pierwotne i renomowane serwisy.
3. Nie wymyślaj faktów, liczb ani linków. Jeśli czegoś nie udało się potwierdzić, napisz „brak danych”.
4. Rozróżniaj fakty od opinii. Nie udzielaj porad inwestycyjnych ani rekomendacji kupna lub sprzedaży.
5. Podane niżej ceny i zmiany pochodzą z danych wejściowych. Nie zgaduj brakujących wartości.

DANE Z KONFIGURACJI
Waluta bazowa: {currency}
Kryptowaluty i tygodniowe ceny:
{crypto_block}

Pozostałe instrumenty i obserwowane rynki:
{instruments_block}

ZADANIA
## CZĘŚĆ 1 – KRYPTOWALUTY
Dla każdej kryptowaluty podaj przekazane ceny i zmianę, najważniejsze wiadomości z tygodnia, możliwe źródła ruchu ceny oraz krótką ocenę nastrojów popartą źródłami. Gdy brak danych, zaznacz to.

## CZĘŚĆ 2 – POZOSTAŁE INSTRUMENTY
Dla każdego instrumentu z listy podaj maksymalnie 3–5 najważniejszych wiadomości z okresu. Dopasuj informacje do rodzaju instrumentu.

## CZĘŚĆ 3 – INFORMACJE GOSPODARCZE I RYNKOWE
Opisz zmiany USD wobec {local_currency} i EUR oraz DXY; decyzje banków centralnych ({banks}); ważne dane makroekonomiczne; rentowności obligacji 10-letnich USA, Niemiec{poland_yield}; główne indeksy giełdowe; Brent i złoto; oraz istotne wydarzenia geopolityczne i sektorowe. Podawaj liczby i źródła. Wskaż jedną najpopularniejszą akcję tygodnia, jasno określając kryterium wyboru.{extra_topics_block}

## CZĘŚĆ 4 – KALENDARZ NA NASTĘPNY TYDZIEŃ
Wypisz chronologicznie ważne publikacje makroekonomiczne, decyzje banków centralnych, wyniki spółek, wydarzenia dotyczące instrumentów z konfiguracji, wydarzenia kryptowalutowe i dni wolne od handlu. Dla każdego podaj datę, godzinę i strefę (jeśli znane), kategorię, opis, znaczenie i źródło. Niepotwierdzone daty oznacz jako takie.

## CZĘŚĆ 5 – PODSUMOWANIE
Podaj pięć najważniejszych wniosków tygodnia, trzy ryzyka lub kwestie do obserwowania w kolejnym tygodniu oraz listę informacji, których nie udało się potwierdzić.

FORMAT
Używaj Markdown, nagłówków dla pięciu części i podnagłówków dla instrumentów. Kalendarz przedstaw jako tabelę: Data, Godzina, Kategoria, Wydarzenie, Dlaczego ważne, Źródło. Linki zapisuj jako [nazwa źródła](URL) z datą publikacji. Nie dodawaj wstępu ani zakończenia poza pięcioma częściami.
"""
