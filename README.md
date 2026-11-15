# Aviava – grupa lotnicza z Iławy

Strona grupy Aviava: [aviava.14-200.pl](https://aviava.14-200.pl). Strona główna opisuje grupę. Pod adresem `/wiki/` jest baza wiedzy o lotnictwie w Iławie, powiecie iławskim i regionie Jezioraka.

Wiki zawiera tylko informacje. Każda informacja ma przypis do strony źródła.

## Struktura

| Ścieżka | Zawartość |
| --- | --- |
| `CLAUDE.md` | Schemat wiki: typy stron, format, zasady i operacje (ingest, query, lint). |
| `raw/` | Surowe źródła: artykuły, PDF, skany, notatki. Pliki się nie zmieniają. |
| `wiki/index.md` | Katalog wszystkich stron. |
| `wiki/log.md` | Rejestr zmian. |
| `wiki/otwarte-pytania.md` | Luki w wiedzy i informacje do sprawdzenia. |
| `wiki/tematy/` | Tematy: historia, prawo, problemy. |
| `wiki/podmioty/` | Aerokluby, lądowiska, wydarzenia. |
| `wiki/zrodla/` | Jedna strona na jedno źródło. |
| `site/home.html` | Strona główna: misja, pierwsza edycja, znak, kontakt. |
| `site/znak.html` | Podstrona `/znak/`: symbolika znaku, wersja jasna i ciemna, kolory, pliki do pobrania. |
| `site/` | Arkusz stylów, fonty (Brygada 1918, Lato), mapa. |
| `marka/` | Znak Aviava: księga znaku (`README.md`), tokeny kolorów, logotypy SVG i PNG, wersja do haftu, grafiki do mediów społecznościowych, generator. |
| `build.mjs` | Generator strony WWW: `wiki/` → `dist/`. |

## Dodanie informacji

1. Dodaj plik do `raw/` albo podaj adres źródła.
2. Agent dodaje stronę źródła w `wiki/zrodla/`, aktualizuje strony tematów i podmiotów, `index.md` i `log.md`.

Szczegóły: `CLAUDE.md`.

## Budowanie

```bash
npm install
node build.mjs
```

Wynik jest w `dist/`. Podgląd: `python3 -m http.server -d dist 8000`, potem `http://localhost:8000/`.

Generator zatrzymuje się z błędem, gdy link `[[slug]]` prowadzi do strony, której nie ma.

## Wdrożenie

Vercel: polecenie budowania `node build.mjs`, katalog wyjściowy `dist` (plik `vercel.json`). Push do `main` uruchamia wdrożenie.

Strony mają znacznik `noindex`. Usuń go w `build.mjs`, gdy wiki ma trafić do wyszukiwarek.
