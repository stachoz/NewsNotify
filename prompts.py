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

Sekcja 'Portfel': aktualne ceny bądź notowania wykorzystaj znane ceny podane wcześniej jeśli są dostępne; oraz podaj najnowszy wskaźnik CPI (GUS) i nadchodzące publikacje danych o inflacji wpływające na oprocentowanie kolejnych rocznic. 

Sekcja 'Podobne instrumenty': tylko istotne zmiany dotyczące porównywalnych instrumentów — np jeśli portfel zawiera krytpowaluty podaj inne duże kryptowaluty przy wyraźnych ruchach rynkowych oraz lub jeśli zawiera obligajce inne serie polskich obligacji detalicznych (np. COI, EDO, DOR) — zawsze z wyjaśnieniem związku z portfelem użytkownika. Nie rob wyczerpującego przeglądu całego rynku.

Sekcja 'Kontekst rynkowy': najważniejsze wydarzenia tygodnia na rynkach np dla krypto (regulacje, ETF-y, duże ruchy instytucjonalne) oraz makro wpływające na portfel (stopy procentowe NBP i Fed, inflacja, USD/PLN, nastroje na rynkach).

Sekcja 'Na co zwrócić uwagę': nadchodzące w najbliższym tygodniu publikacje makro, decyzje banków centralnych lub wydarzenia istotne dla portfela.

Zasady: każdy fakt musi być poparty źródłem z bezpośrednim linkiem; wybieraj tylko istotne zmiany, nie wypełniaj raportu starymi wiadomościami; jeśli w danym tygodniu nic istotnego się nie zmieniło, napisz to krótko; raport zwięzły (maks. kilka sekcji). Jeżeli dla jakiegoś instrumentu ceny są dostępne nie wyszukuj ich w internecie tylko wykorzystaj te podane.
    
    """