# Generator znaku Aviava

Wymagania: Python 3.10+, shapely 2.x, fonttools, uharfbuzz, cairosvg, numpy, scipy, Pillow. Fonty w katalogu fonts/.

- logo2.py – znak i zastosowania
- haft.py – wersja do haftu dla Ink/Stitch
- drc.py – kontrola reguł haftu
- social.py – grafiki do mediów społecznościowych
- wings.py – propozycje ze skrzydłami
- swans.py, jeziorak_data.py, lake_build.py, logo.py – ptaki, obrys jezior, napisy z kerningiem
- export.py – eksport SVG i PNG

Użycie: python export.py; python social.py (z katalogu generator/).
