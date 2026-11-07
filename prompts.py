from datetime import date, timedelta

def get_weekly_prompt(config, crypto_data=None):
    today = date.today()
    date_from, date_to = today - timedelta(days=7), today

    return f"""
DZISIEJSZA DATA: {today:%Y-%m-%d}
OKRES PRZEGLĄDU: {date_from:%Y-%m-%d} – {date_to:%Y-%m-%d}
Przygotuj cotygodniowy raport rynkowy w języku polskim dla użytkownika. Jego portfel: {config.get("holdings", [])}
Informacje o instrumentach zebrane z API: {crypto_data}

Raport ma zawierać:

Sekcja 'Portfel': aktualne ceny bądź notowania - wykorzystaj znane ceny podane wcześniej jeśli są dostępne, w przeciwnym wypadku krótko o tym poinformuj.

Sekcja 'Kontekst rynkowy': najważniejsze wydarzenia tygodnia na rynkach np dla krypto (regulacje, ETF-y, duże ruchy instytucjonalne) oraz makro wpływające na portfel (stopy procentowe NBP i Fed, inflacja, USD/PLN, nastroje na rynkach).

Sekcja 'Na co zwrócić uwagę': nadchodzące w najbliższym tygodniu publikacje makro, decyzje banków centralnych lub wydarzenia istotne dla portfela.

Zasady: każdy fakt musi być poparty źródłem z bezpośrednim linkiem; wybieraj tylko istotne zmiany, nie wypełniaj raportu starymi wiadomościami; jeśli w danym tygodniu nic istotnego się nie zmieniło, napisz to krótko; raport zwięzły (maks. kilka sekcji). Jeżeli dla jakiegoś instrumentu ceny są dostępne nie wyszukuj ich w internecie tylko wykorzystaj te podane.
    
    """

def get_kobeisii_letter_summarization_prompt():
    return f"""Podsumuj tweety w ostatnim tygodniu zamieszczone przez The Kobeissi Letter. Podaj najważniejsze które powinienem samodzielnie przeczytać w całości"""