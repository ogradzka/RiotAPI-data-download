## Opis Projektu
**League of Legends Data Collector** to narzędzie napisane w Pythonie, które korzysta z Riot Games Developer API do pobierania i wstępnej analizy danych meczowych graczy znajdujących się na zdefiniowanej liście. Projekt umożliwia zbieranie szczegółowych statystyk z meczów i zapisywanie ich do pliku CSV, co ułatwia dalszą analizę.

---

## Funkcjonalności
- **Pobieranie PUUID graczy:** Automatyczne pobieranie unikalnych identyfikatorów graczy na podstawie ich nazw i tagów.
- **Zbieranie danych meczowych:** Pobieranie identyfikatorów meczów i szczegółowych danych o rozgrywkach.
- **Analiza timeline:** Wyciąganie statystyk z pierwszych 15 minut meczu.
- **Zarządzanie limitami zapytań:** Narzędzie przestrzega limitów narzuconych przez Riot API.
- **Eksport danych:** Zapisywanie zebranych danych w formacie CSV, gotowym do użycia w narzędziach analitycznych.

---

## Wymagania
- **Python 3.8+**
- Wymagane biblioteki Python:
  - `os`
  - `requests`
  - `dotenv`
  - `time`
  - `csv`
  - `collections` (deque)
- **Klucz API Riot Games:**
  Uzyskaj klucz API na stronie [Riot Developer Portal](https://developer.riotgames.com/).
- **Utwórz plik `.env`:**
   Dodaj swój klucz API Riot do pliku `.env` w głównym katalogu projektu:
   ```env
   RIOT_API_KEY=twoj-klucz-api
   ```
---

## Użycie
1. **Uruchom skrypt główny:**
2. **Wyniki:**
   - Skrypt utworzy lub uzupełni plik `match_data.csv` w głównym katalogu.
   - Plik CSV będzie zawierał szczegółowe dane o meczach, w tym statystyki graczy i drużyn.

---

## Struktura CSV
Plik wynikowy CSV zawiera następujące kolumny:
- `match_id`
- `game_duration`
- `blue_win`, `red_win`
- Statystyki drużyn (np. `blueGold`, `blueMinionsKilled`, itp.)
- Statystyki graczy (np. `summoner_name`, `kills`, `deaths`, `assists`, itp.)

---

## Główne funkcje
- **`get_puuid_by_name_and_tag(name, tag)`**
  - Pobiera PUUID dla podanej nazwy gracza i tagu.
- **`get_match_ids(puuid, count)`**
  - Pobiera identyfikatory meczów dla określonego gracza.
- **`get_match_data(match_id)`**
  - Pobiera szczegółowe dane dla danego meczu.
- **`get_match_timeline(match_id)`**
  - Pobiera timeline wydarzeń dla meczu.
- **`extract_data_from_timeline(timeline_data, match_data)`**
  - Analizuje dane timeline, wyciągając kluczowe statystyki z początkowej fazy gry.
- **`save_to_csv(data, filename)`**
  - Zapisuje zebrane dane do pliku CSV.

---

## Limity zapytań
Aby przestrzegać ograniczeń Riot API:
- **Maksymalnie 20 zapytań na sekundę**
- **Maksymalnie 100 zapytań na 2 minuty**
- Skrypt automatycznie czeka, gdy limit zostanie osiągnięty.

---

## Licencja
Projekt jest objęty licencją MIT. Szczegóły znajdziesz w pliku `LICENSE`.

---

## Podziękowania
- Riot Games za udostępnienie API i danych.
