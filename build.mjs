// Makes the web site in dist/ from the Markdown pages in wiki/.
// Usage: node build.mjs
import fs from 'node:fs';
import path from 'node:path';
import { Marked } from 'marked';
import markedFootnote from 'marked-footnote';

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const WIKI = path.join(ROOT, 'wiki');
const SITE = path.join(ROOT, 'site');
const DIST = path.join(ROOT, 'dist');
const SITE_NAME = 'Lotnictwo – Iława i powiat iławski';

// ---- Read all pages -------------------------------------------------------
function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? walk(p) : e.name.endsWith('.md') ? [p] : [];
  });
}

function parseFrontMatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?/);
  const meta = {};
  if (!m) return { meta, body: text };
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (!kv) continue;
    let v = kv[2].trim();
    if (v.startsWith('[') && v.endsWith(']')) v = v.slice(1, -1).split(',').map((s) => s.trim()).filter(Boolean);
    else if (v.startsWith('"') && v.endsWith('"')) v = v.slice(1, -1);
    meta[kv[1]] = v;
  }
  return { meta, body: text.slice(m[0].length) };
}

const pages = new Map(); // slug -> page
for (const file of walk(WIKI)) {
  const rel = path.relative(WIKI, file).replace(/\\/g, '/');
  const slug = path.basename(rel, '.md');
  if (pages.has(slug)) throw new Error(`Duplicate slug: ${slug}`);
  const { meta, body } = parseFrontMatter(fs.readFileSync(file, 'utf8'));
  const dir = path.dirname(rel);
  const url = slug === 'index' ? '/' : dir === '.' ? `/${slug}/` : `/${dir}/${slug}/`;
  pages.set(slug, { slug, rel, url, meta, body, title: meta.title || slug, links: new Set() });
}

// ---- Wiki links -----------------------------------------------------------
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const errors = [];

function resolveLinks(page) {
  return page.body.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target, text) => {
    const t = pages.get(target.trim());
    if (!t) {
      errors.push(`${page.rel}: unknown link [[${target}]]`);
      return text || target;
    }
    page.links.add(t.slug);
    return `[${(text || t.title).replace(/([\[\]])/g, '\\$1')}](${t.url})`;
  });
}

for (const p of pages.values()) p.md = resolveLinks(p);
if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}

const backlinks = new Map();
for (const p of pages.values()) for (const s of p.links) {
  if (!backlinks.has(s)) backlinks.set(s, []);
  backlinks.get(s).push(p);
}

// ---- HTML -----------------------------------------------------------------
const CSS = fs.readFileSync(path.join(SITE, 'style.css'), 'utf8');

function layout({ title, url, content, head = '', tail = '' }) {
  return `<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${esc(url === '/' ? SITE_NAME : `${title} – ${SITE_NAME}`)}</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>${CSS}</style>
${head}</head>
<body>
<header class="bar"><a class="name" href="/">${esc(SITE_NAME)}</a>
<nav><a href="/">Indeks</a> <a href="/mapa/">Mapa</a> <a href="/otwarte-pytania/">Otwarte pytania</a> <a href="/log/">Zmiany</a></nav></header>
<main>
${content}
</main>
<footer>Wiki. Każda informacja ma przypis do źródła. Poprawki: <a href="mailto:aeroklub@14-200.pl">aeroklub@14-200.pl</a>. Kod: <a href="https://github.com/yasiupl/aeroklub">github.com/yasiupl/aeroklub</a>. Strona nie używa ciasteczek.</footer>
${tail}</body>
</html>
`;
}

function render(p) {
  const marked = new Marked({ gfm: true });
  marked.use(markedFootnote({ description: 'Przypisy', refMarkers: true }));
  let html = marked.parse(p.md);
  const info = [];
  if (p.meta.type) info.push({ temat: 'Temat', podmiot: 'Podmiot', zrodlo: 'Źródło' }[p.meta.type] || p.meta.type);
  if (p.meta.published) info.push(`opublikowano: ${esc(p.meta.published)}`);
  if (p.meta.accessed) info.push(`odczytano: ${esc(p.meta.accessed)}`);
  if (p.meta.updated) info.push(`aktualizacja: ${esc(p.meta.updated)}`);
  const back = (backlinks.get(p.slug) || []).filter((b) => b.slug !== 'index' && b.slug !== p.slug);
  if (p.slug !== 'index' && back.length) {
    html += `<section class="backlinks"><h2>Linkujące strony</h2><ul>${back
      .sort((a, b) => a.title.localeCompare(b.title, 'pl'))
      .map((b) => `<li><a href="${b.url}">${esc(b.title)}</a></li>`)
      .join('')}</ul></section>`;
  }
  if (p.slug !== 'index') html = html.replace('</h1>', `</h1>\n<p class="meta">${info.join(' · ')} · <a href="https://github.com/yasiupl/aeroklub/blob/main/wiki/${p.rel}">źródło strony</a></p>`);
  return layout({ title: p.title, url: p.url, content: html });
}

// ---- Write ----------------------------------------------------------------
fs.rmSync(DIST, { recursive: true, force: true });
function out(url, html) {
  const dir = path.join(DIST, url);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'index.html'), html);
}
for (const p of pages.values()) out(p.url, render(p));

// Map page
const mapContent = `<h1>Mapa: aerokluby, lądowiska i dojazdy z Iławy</h1>
<p>Czerwony obszar: powiat iławski bez lądowiska dla samolotów i szybowców (<a href="/tematy/biala-plama/">biała plama</a>). Współrzędne lotnisk pochodzą ze stron źródeł. Drogę i czas jazdy liczy serwer OSRM na podstawie danych OpenStreetMap, bez korków.</p>
<div id="mapa" class="map" role="region" aria-label="Mapa"></div>
<h2>Dojazdy z Iławy</h2>
<div class="table-wrap"><table><thead><tr><th>Aeroklub</th><th>Lotnisko</th><th>Linia prosta</th><th>Droga</th><th>Czas jazdy</th></tr></thead><tbody id="dojazdy"></tbody></table></div>`;
out('/mapa/', layout({
  title: 'Mapa',
  url: '/mapa/',
  content: mapContent,
  head: '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">\n',
  tail: '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>\n<script src="/mapa/mapa.js"></script>\n',
}));
fs.copyFileSync(path.join(SITE, 'mapa.js'), path.join(DIST, 'mapa', 'mapa.js'));
fs.copyFileSync(path.join(SITE, 'powiat-ilawski.geojson'), path.join(DIST, 'mapa', 'powiat-ilawski.geojson'));
fs.copyFileSync(path.join(SITE, 'favicon.svg'), path.join(DIST, 'favicon.svg'));

console.log(`Built ${pages.size} pages and the map into dist/.`);
