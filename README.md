# Skrzydła nad Jeziorakiem

Wizytówka grupy lotniczej z Iławy i powiatu iławskiego. Adres: [aeroklub.14-200.pl](https://aeroklub.14-200.pl).

Witryna jest bazą wiedzy grupy: opis celów, historia lotnictwa w regionie i mapa dojazdów do aeroklubów.

## Struktura

| Ścieżka | Zawartość |
| --- | --- |
| `index.html` | Opis grupy: cele, zasady i kierunki działania. |
| `historia/index.html` | Artykuł o historii lotnictwa w regionie. |
| `mapa/index.html` | Mapa dojazdów do aeroklubów i obszaru bez lądowiska. |
| `mapa/mapa.js` | Dane i logika mapy: aerokluby, lądowiska, trasy. |
| `mapa/powiat-ilawski.geojson` | Uproszczona granica powiatu iławskiego. |
| `style.css` | Wspólny arkusz stylów. Kolory są w zmiennych na `:root`. |
| `vercel.json` | Konfiguracja wdrożenia. |

## Technologia

* Statyczne pliki HTML i CSS. Witryna nie wymaga kroku budowania.
* Mapa używa biblioteki [Leaflet](https://leafletjs.com) z cdnjs i podkładu [OpenStreetMap](https://www.openstreetmap.org).
* Trasy drogowe liczy publiczny serwer [OSRM](https://project-osrm.org) w przeglądarce odwiedzającego. Gdy serwer nie odpowiada, mapa rysuje linię prostą.
* Ikony: Font Awesome z cdnjs. Kroje pisma: Inter i Merriweather z Google Fonts.
* Witryna nie używa ciasteczek ani analityki.

## Zmiany w treści

1. Pisz krótkie zdania. Jedno słowo ma jedno znaczenie.
2. Każdy fakt historyczny lub liczba ma źródło w sekcji „Źródła” na tej samej stronie.
3. Nie publikuj prywatnych numerów telefonów ani adresów osób prywatnych. Podaj link do strony organizacji.
4. Aby dodać aeroklub lub lądowisko do mapy, dopisz wpis do tablicy `AEROKLUBY` lub `LADOWISKA` w `mapa/mapa.js`.

## Uruchomienie lokalne

Uruchom prosty serwer w katalogu repozytorium:

```bash
python3 -m http.server 8000
```

Otwórz `http://localhost:8000/`. Linki na stronach zaczynają się od `/`, więc otwarcie pliku bezpośrednio z dysku nie działa.

## Wdrożenie

Witrynę hostuje Vercel. Push do gałęzi `main` uruchamia wdrożenie produkcyjne. Push do innej gałęzi tworzy wdrożenie podglądowe.

## Widoczność w wyszukiwarkach

Strony z wersją roboczą mają znacznik `<meta name="robots" content="noindex">`. Usuń znacznik, gdy treść jest gotowa do publikacji.
