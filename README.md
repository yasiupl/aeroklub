# Skrzydła nad Jeziorakiem

Wizytówka inicjatywy lotniczej z Iławy i powiatu iławskiego. Adres: [aeroklub.14-200.pl](https://aeroklub.14-200.pl).

Witryna jest bazą wiedzy w stylu wiki. Zbiera argumenty za aeroklubem i lądowiskiem w regionie.

## Struktura

| Ścieżka | Zawartość |
| --- | --- |
| `index.html` | Strona główna: argumenty za aeroklubem w regionie i cele inicjatywy. |
| `historia/index.html` | Historia lotnictwa: w Polsce, w regionie, w Iławie po 1945 roku i przed 1945 rokiem. |
| `mapa/index.html` | Stan obecny: mapa aeroklubów i lądowisk, czasy dojazdu, biała plama. |
| `mozliwosci/index.html` | Możliwości: szkolenie, wydarzenia, forma organizacji, lądowisko. |
| `wspolpraca/index.html` | Propozycja współpracy dla aeroklubów. |
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
2. Publikuj tylko informacje sprawdzone w źródle. Każdy fakt ma przypis `[n]` do listy „Źródła” na tej samej stronie.
3. Stanowisko i plany inicjatywy umieszczaj w ramce „Stanowisko inicjatywy” (`.stance`). Nie mieszaj ich z faktami.
4. Historię sprzed 1945 roku (Deutsch Eylau) opisuj osobno, jako ciekawostkę historyczną.
5. Nie publikuj prywatnych numerów telefonów ani adresów osób prywatnych. Podaj link do strony organizacji.
6. Aby dodać aeroklub lub lądowisko do mapy, dopisz wpis do tablicy `AEROKLUBY` lub `LADOWISKA` w `mapa/mapa.js`.

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
