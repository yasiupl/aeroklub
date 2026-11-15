// Makes the web site in dist/: the home page from site/home.html and the wiki pages from wiki/.
// Usage: node build.mjs
import fs from 'node:fs';
import path from 'node:path';
import { Marked } from 'marked';
import markedFootnote from 'marked-footnote';

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const WIKI = path.join(ROOT, 'wiki');
const SITE = path.join(ROOT, 'site');
const DIST = path.join(ROOT, 'dist');
const MARKA = path.join(ROOT, 'marka');
const SITE_URL = 'https://aviava.14-200.pl';
const SITE_NAME = 'Aviava';
const HOME_TITLE = 'Aviava – grupa lotnicza z regionu Iławy';
const HOME_DESC = 'Aviava to grupa lotnicza z regionu Iławy. Zaczynamy od szybowców: teoria w Iławie, praktyka w szkole partnerskiej.';
const WIKI_NAME = 'Baza wiedzy Aviava';
const WIKI_URL = '/wiki'; // URL prefix of the wiki
// Visitor statistics: self-hosted Plausible at plausible.yasiu.pl (no cookies, no personal data).
// The snippet comes from the site settings in the Plausible dashboard; the script file is specific to this site.
const PLAUSIBLE = `<!-- Privacy-friendly analytics by Plausible -->
<script async src="https://plausible.yasiu.pl/js/pa-qmN6ge7u7juRv2pQF8HLn.js"></script>
<script>
  window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
  plausible.init()
</script>`;

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
  const url = slug === 'index' ? `${WIKI_URL}/` : dir === '.' ? `${WIKI_URL}/${slug}/` : `${WIKI_URL}/${dir}/${slug}/`;
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
// Colour variables come from the brand tokens. Theme "light" is the default for everyone.
// Theme "dark" is on only when the visitor turns it on with the switch in the header (data-theme="dark").
const tokens = JSON.parse(fs.readFileSync(path.join(MARKA, 'tokens.json'), 'utf8')).color.tokens;
const vars = (theme) => tokens.map((t) => `--${t.name}:${t.value[theme]}`).join(';');
const CSS = `:root{color-scheme:light;${vars('light')}}\n:root[data-theme="dark"]{color-scheme:dark;${vars('dark')}}\n`
  + fs.readFileSync(path.join(SITE, 'style.css'), 'utf8');
const THEME_KEY = 'aviava-motyw';
// Runs in <head> before the page is drawn, so the saved theme does not flash.
const THEME_HEAD = `<script>try{if(localStorage.getItem('${THEME_KEY}')==='dark')document.documentElement.dataset.theme='dark'}catch(e){}</script>`;
const THEME_SWITCH = `<button class="theme" type="button" aria-pressed="false" hidden><span class="vh">Wersja ciemna</span><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path class="moon" d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z"/><g class="sun"><circle cx="12" cy="12" r="4.5"/><path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/></g></svg></button>`;
const THEME_TAIL = `<script>(function(){var b=document.querySelector('.theme'),r=document.documentElement;if(!b)return;b.hidden=false;
function set(d){if(d)r.dataset.theme='dark';else delete r.dataset.theme;b.setAttribute('aria-pressed',d?'true':'false');b.title=d?'Wersja jasna':'Wersja ciemna';}
set(r.dataset.theme==='dark');b.addEventListener('click',function(){var d=r.dataset.theme!=='dark';set(d);try{if(d)localStorage.setItem('${THEME_KEY}','dark');else localStorage.removeItem('${THEME_KEY}')}catch(e){}});})();</script>`;
// Logo in both versions: CSS shows the one that matches the theme.
const both = (name, dark, attrs) => `<img class="v-light" src="/marka/${name}.svg" ${attrs}><img class="v-dark" src="/marka/${dark}.svg" ${attrs}>`;

const NAV = [
  ['/', 'Start'],
  ['/znak/', 'Znak'],
  [`${WIKI_URL}/`, 'Baza wiedzy'],
  [`${WIKI_URL}/mapa/`, 'Mapa'],
  ['/kontakt/', 'Kontakt'],
];

function layout({ title, url, content, head = '', tail = '', home = false, page = false, description = '' }) {
  const fullTitle = home ? HOME_TITLE : page ? `${title} – ${SITE_NAME}` : url === `${WIKI_URL}/` ? WIKI_NAME : `${title} – ${WIKI_NAME}`;
  const section = home || page || url === `${WIKI_URL}/mapa/` ? url : `${WIKI_URL}/`;
  const nav = NAV.map(([href, text]) => `<a href="${href}"${href === section ? ' aria-current="page"' : ''}>${text}</a>`).join(' ');
  return `<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${esc(fullTitle)}</title>
${description ? `<meta name="description" content="${esc(description)}">\n` : ''}<meta property="og:title" content="${esc(fullTitle)}">
<meta property="og:type" content="website">
<meta property="og:url" content="${SITE_URL}${url}">
<meta property="og:image" content="${SITE_URL}/marka/aviava-tlo.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
${PLAUSIBLE}
<link rel="preload" href="/fonts/brygada1918-bold.woff2" as="font" type="font/woff2" crossorigin>
${THEME_HEAD}
<style>${CSS}</style>
${head}</head>
<body${home || page ? ' class="home"' : ''}>
<header class="bar"><div class="bar-in"><a class="name" href="/">${both('aviava-sygnet', 'aviava-sygnet-ciemny', 'alt="" width="40" height="40"')}${esc(SITE_NAME)}</a>
<nav aria-label="Główna">${nav}</nav>${THEME_SWITCH}</div></header>
<main>
${content}
</main>
<footer><div class="in">
<p>Aviava – grupa lotnicza z regionu Iławy. <a href="/kontakt/">Kontakt</a></p>
<p>Wykonanie: <a href="https://14-200.pl">14-200.pl</a>. Strona nie używa ciasteczek.</p>
</div></footer>
${THEME_TAIL}
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
  if (p.slug !== 'index') html = `<p class="crumb"><a href="${WIKI_URL}/">Baza wiedzy</a></p>\n` + html;
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

// Home page
const withLogos = (html) => html.replace(/\{\{logo:([\w-]+):([\w-]+):([^}]*)\}\}/g, (_, a, b, attrs) => both(a, b, attrs));
out('/', layout({ title: HOME_TITLE, url: '/', home: true, description: HOME_DESC, content: withLogos(fs.readFileSync(path.join(SITE, 'home.html'), 'utf8')) }));

// Brand page: the colour table comes from marka/tokens.json
const SWATCHES = [
  ['rim', 'Obrzeże'], ['band', 'Otok'], ['field', 'Pole'], ['water', 'Woda'], ['town', 'Iława'], ['lettering', 'Napisy'],
];
const tok = Object.fromEntries(tokens.map((t) => [t.name, t.value]));
const swatchRow = (theme, name) => `<div class="palette"><p class="pal-name">${name}</p><ul>${SWATCHES.map(([k, label]) =>
  `<li><span class="chip" style="background:${tok[k][theme]}"></span><b>${label}</b><code>${tok[k][theme]}</code></li>`).join('')}</ul></div>`;
const paleta = swatchRow('light', 'Wersja jasna') + swatchRow('dark', 'Wersja ciemna')
  + `<div class="palette"><p class="pal-name">Fale (flaga, proporczyk)</p><ul>${[['flag-blue', 'Niebieski'], ['flag-white', 'Biały']].map(([k, label]) =>
    `<li><span class="chip" style="background:${tok[k].light}"></span><b>${label}</b><code>${tok[k].light}</code></li>`).join('')}</ul></div>`;
out('/kontakt/', layout({
  title: 'Kontakt', url: '/kontakt/', page: true,
  description: 'Kontakt z Aviavą: aviava@14-200.pl. Zapisy, współpraca, media.',
  content: fs.readFileSync(path.join(SITE, 'kontakt.html'), 'utf8'),
}));
out('/zapisy/', layout({
  title: 'Zapisy', url: '/zapisy/', page: true,
  description: 'Zapisz się do Aviavy: szybowce w Iławie, zajęcia teoretyczne, spotkania i wyjazdy na lotnisko.',
  content: fs.readFileSync(path.join(SITE, 'zapisy.html'), 'utf8'),
}));
out('/znak/', layout({
  title: 'Znak', url: '/znak/', page: true,
  description: 'Znak Aviava: symbolika, wersja jasna i ciemna, kolory, typografia i pliki do pobrania.',
  content: fs.readFileSync(path.join(SITE, 'znak.html'), 'utf8').replace('{{paleta}}', paleta),
}));

// Map page
const MAP_URL = `${WIKI_URL}/mapa/`;
const mapContent = `<p class="crumb"><a href="${WIKI_URL}/">Baza wiedzy</a></p>
<h1>Mapa: aerokluby, lądowiska i dojazdy z Iławy</h1>
<p>Czerwony obszar: powiat iławski bez lądowiska dla samolotów i szybowców (<a href="${WIKI_URL}/tematy/biala-plama/">biała plama</a>).</p>
<div id="mapa" class="map" role="region" aria-label="Mapa"></div>
<h2>Dojazdy z Iławy</h2>
<div class="table-wrap"><table><thead><tr><th>Aeroklub</th><th>Lotnisko</th><th>Linia prosta</th><th>Droga</th><th>Czas jazdy</th></tr></thead><tbody id="dojazdy"></tbody></table></div>
<p class="meta">Współrzędne lotnisk pochodzą ze stron źródeł. Drogę i czas jazdy liczy serwer OSRM na podstawie danych OpenStreetMap, bez korków.</p>`;
out(MAP_URL, layout({
  title: 'Mapa',
  url: MAP_URL,
  content: mapContent,
  head: '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">\n',
  tail: `<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>\n<script src="${MAP_URL}mapa.js"></script>\n`,
}));
const copy = (from, to) => {
  fs.mkdirSync(path.dirname(path.join(DIST, to)), { recursive: true });
  fs.copyFileSync(from, path.join(DIST, to));
};
copy(path.join(SITE, 'mapa.js'), `${MAP_URL}mapa.js`);
copy(path.join(SITE, 'powiat-ilawski.geojson'), `${MAP_URL}powiat-ilawski.geojson`);

// Brand files and fonts
for (const n of ['naszywka-jasna', 'naszywka-ciemna', 'sygnet', 'sygnet-ciemny', 'flaga', 'proporczyk', 'odznaka']) {
  copy(path.join(MARKA, 'svg', `aviava-${n}.svg`), `/marka/aviava-${n}.svg`);
  copy(path.join(MARKA, 'png', `aviava-${n}-2048.png`), `/marka/aviava-${n}-2048.png`);
}
copy(path.join(MARKA, 'media-spolecznosciowe', 'facebook-tlo-jasna.png'), '/marka/aviava-tlo.png');
copy(path.join(MARKA, 'svg', 'aviava-sygnet.svg'), '/favicon.svg');
for (const f of fs.readdirSync(path.join(SITE, 'fonts'))) copy(path.join(SITE, 'fonts', f), `/fonts/${f}`);
for (const f of fs.readdirSync(path.join(SITE, 'img'))) copy(path.join(SITE, 'img', f), `/img/${f}`);

console.log(`Built the home page, the brand page, ${pages.size} wiki pages and the map into dist/.`);
