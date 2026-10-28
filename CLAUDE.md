# Wiki schema

This repository is a wiki about aviation in Iława and the Iława county (powiat iławski), Poland. The wiki follows the "LLM wiki" pattern: an agent reads raw sources and keeps a set of linked Markdown pages up to date.

The wiki contains information only. It does not contain offers, plans, or opinions of any organization.

## Layers

| Folder | Content | Who writes |
| --- | --- | --- |
| `raw/` | Source files: articles, PDF files, scans, photos, notes from conversations. | The user. The agent does not change or delete these files. |
| `wiki/` | Markdown pages. The agent writes and updates them. | The agent. |
| `site/` | Files for the web site: the map script and static files. | The agent. |
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
- Each page has a list of pages that link to it ("Linkujące strony").
- The site has the meta tag `noindex`. Remove it from `build.mjs` when the wiki is public.
- The map (`site/mapa.js`) uses Leaflet, OpenStreetMap and the public OSRM server. Coordinates in the map must have a source page.
