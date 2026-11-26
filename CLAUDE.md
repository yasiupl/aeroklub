# Wiki schema

This repository is the web site of Aviava, an aviation group from Iława (address: aviava.14-200.pl). The site has a home page about the group and a wiki about aviation in Iława and the Iława county (powiat iławski), Poland. The wiki follows the "LLM wiki" pattern: an agent reads raw sources and keeps a set of linked Markdown pages up to date.

The wiki contains information only. It does not contain offers, plans, or opinions of any organization. The home page (`site/home.html`) is the only page about the group: its mission, plans and contact. The rules for the text below apply to the wiki, not to the home page.

## Layers

| Folder | Content | Who writes |
| --- | --- | --- |
| `raw/` | Source files: articles, PDF files, scans, photos, notes from conversations. | The user. The agent does not change or delete these files. |
| `wiki/` | Markdown pages. The agent writes and updates them. | The agent. |
| `site/` | Files for the web site: the home page (`home.html`), the brand page (`znak.html`), the sign-up page (`zapisy.html`), the contact page (`kontakt.html`), the news page (`aktualnosci.html`, `aktualnosci.js`), the style, the fonts, the photos (`img/`), the map script and static files. | The agent. |
| `marka/` | Brand files of the Aviava sign: brand book, tokens, logos, embroidery files, social media graphics, generator. Not part of the wiki. The site takes its colours and logos from it. | The generator in `marka/generator/`, with the approval of the user. |
| `build.mjs` | Script that makes HTML pages in `dist/` from `wiki/`. | The agent. |

## Page types

| Folder | Type | Content |
| --- | --- | --- |
| `wiki/tematy/` | `temat` | A subject: a period of history, a law, a problem. |
| `wiki/podmioty/` | `podmiot` | One organization, one airfield, one event or one person in a public role. |
| `wiki/zrodla/` | `zrodlo` | One source: what the source says and where to find it. |
| `wiki/` | – | `index.md` (catalog of all pages), `log.md` (record of changes), `otwarte-pytania.md` (gaps and open questions). |

## Page format

Each page starts with YAML front matter:

```yaml
---
title: Lądowisko Gryźliny
type: podmiot            # temat | podmiot | zrodlo
updated: 2026-10-28
sources: [ulc-wykaz-ladowisk-2026, dlapilota-gryzliny]   # slugs of pages in wiki/zrodla/
---
```

A source page has these extra fields:

```yaml
url: https://...
published: 2026-02-25     # date of the source, if known
accessed: 2026-10-28      # date when the agent read the source
raw: raw/plik.pdf         # copy in raw/, if there is one
```

Rules for the text:

1. Write in Polish. Use short sentences. One word has one meaning.
2. Write only facts that a source supports. Put a footnote after each fact: `[^ulc]`. At the end of the page, define the footnote with a link to the source page: `[^ulc]: [[ulc-wykaz-ladowisk-2026]]`.
3. Do not write offers, plans, opinions or calls to action.
4. If two sources do not agree, write both and give each a footnote. Add the conflict to `otwarte-pytania.md`.
5. Write a calculation (for example, a distance) as a calculation. Give the input data and the method.
6. Describe the history of Iława before 1945 (Deutsch Eylau) on separate pages.
7. Do not publish private telephone numbers or private addresses. Give a link to the page of the organization.

## Links

- Link to other pages with `[[slug]]` or `[[slug|text]]`. The slug is the file name without `.md`. Slugs are unique in all of `wiki/`.
- File names use lowercase letters, digits and `-`. Do not use Polish letters in file names.

## Operations

### Ingest (add a source)

1. Read the new file in `raw/` or the URL.
2. Make a page in `wiki/zrodla/`. Write what the source says, in points. Write the dates `published` and `accessed`.
3. Update or make the `temat` and `podmiot` pages that the source is about. Add footnotes.
4. Add new pages to `index.md`.
5. Add one line to the top of `log.md`: date, operation, source, changed pages.

### Query (answer a question)

1. Read `index.md`. Read the related pages.
2. Answer with links to the pages.
3. If the answer is useful for later, save it as a new page and do the steps of an ingest.

### Lint (check the wiki)

Find and record in `otwarte-pytania.md`:

- facts without a footnote,
- conflicts between sources,
- pages without links to them,
- old facts (for example, a status of an airfield),
- subjects without a page.

## Web site

- `node build.mjs` makes the site in `dist/`. The Vercel project runs this command.
- `vercel-ignore.sh` (Vercel `ignoreCommand`) skips the build when no web site file changed since the last deployment: brand book, generator, social media graphics, photos in `marka/`, `raw/` and the documentation do not start a build. When `build.mjs` reads a new file or folder, add it to the list in `vercel-ignore.sh`.
- The home page is at `/`. The wiki is at `/wiki/`. The map is at `/wiki/mapa/`. `vercel.json` redirects the old wiki addresses (without `/wiki/`).
- Colours: `build.mjs` writes the brand tokens from `marka/tokens.json` as CSS variables. Theme `light` is the default for all visitors. Theme `dark` is on only when the visitor turns it on with the switch in the header (`data-theme="dark"`, saved in `localStorage`). Do not use `prefers-color-scheme`: the dark version of the brand is reserved for the staff and special occasions. Do not write brand colour values in `site/style.css`.
- Logos in two versions: use the `{{logo:light-file:dark-file:attributes}}` placeholder in `site/*.html`. CSS shows the version that matches the theme.
- The contact page (`site/kontakt.html`, address `/kontakt/`) lists the ways to contact the group. The address is aviava@14-200.pl.
- The sign-up page (`site/zapisy.html`, address `/zapisy/`) shows the Google Form in an iframe. `/zapisz` and `/formularz` redirect to it.
- The brand page (`site/znak.html`, address `/znak/`) explains the sign. `{{paleta}}` is the colour table from `marka/tokens.json`.
- Fonts: Brygada 1918 (headings) and Lato (text), files in `site/fonts/`, licence SIL OFL 1.1.
- Each page has a list of pages that link to it ("Linkujące strony").
- News page (`site/aktualnosci.html` and `site/aktualnosci.js`, address `/aktualnosci/`): the official Facebook Page Plugin (timeline) of https://www.facebook.com/profile.php?id=61596575672213, width up to 500 px. It loads only after a click on „Pokaż aktualności z Facebooka”: before the click the site sends no request to Facebook and sets no cookies. Do not load the Facebook SDK or any Facebook file before the click. A fediverse feed will replace this source later; the Facebook plugin stays as the fallback.
- Social media: `SOCIAL` in `build.mjs` (Facebook, Instagram). Icons are inline SVG with the official shapes from simple-icons (CC0 1.0): no external library, no request, no cookies. Footer: icons only, on the right. Pages: `{{social}}` placeholder (icon and text).
- Visitor statistics: self-hosted Plausible at plausible.yasiu.pl, site `aviava.14-200.pl`. `build.mjs` adds the snippet from the Plausible dashboard to every page (`PLAUSIBLE`). Plausible uses no cookies. Do not add other analytics or cookies.
- Search engines and AI: each page has the meta tags `robots` (`index, follow`), `description`, `canonical` and Open Graph, and structured data (schema.org JSON-LD: `Organization`, `WebSite`, `WebPage` or `Article`). `build.mjs` makes `sitemap.xml`, `robots.txt` and `llms.txt` in `dist/`. Do not add a `robots.txt` file to `site/`.
- The description of a wiki page is the field `description` in the front matter. If the page does not have this field, `build.mjs` uses the first lines of text (maximum 160 characters). Write `description` when the first lines do not describe the page.
- The date in `sitemap.xml` is the field `updated` of the page. Keep `updated` correct.
- A link from a wiki page to the map is `/wiki/mapa/`.
- The map (`site/mapa.js`) uses Leaflet, OpenStreetMap and the public OSRM server. Coordinates in the map must have a source page.
