#!/usr/bin/env node
/*
 * Writes each static diagram as a standalone SVG image under exports/.
 *
 * A consumer that cannot inline HTML or run script (a Docusaurus site, a
 * README, a GitHub preview) references the exported file as an image. The
 * export is lossless only because the static kind forbids script, SMIL, and
 * CSS motion (enforced by validate.js): what remains is markup plus scoped
 * style, and both survive inside an <svg> rendered through <img>.
 *
 * The fragment's root <div> supplies the panel (background, radius, padding)
 * in the blog; here a <rect> supplies it, the <style> moves inside the
 * <svg>, and the root class moves onto the <svg> so every scoped selector
 * still matches. Output is deterministic, and exports/ is committed, so a
 * diagram edit shows its image diff in the same pull request, and the
 * manifest's consumers list names each repository that must re-copy it.
 *
 * Usage:
 *   node scripts/export-svg.js                    # every static diagram -> exports/
 *   node scripts/export-svg.js --check            # fail if exports/ is stale
 *   node scripts/export-svg.js --file diagrams/<slug>/<name>.html
 *   node scripts/export-svg.js --out <dir>        # default: exports/
 */
'use strict';

const fs = require('fs');
const path = require('path');
const F = require('./lib/fragment');
const cli = require('./lib/cli');
const { report } = require('./lib/report');

const USAGE = 'usage: node scripts/export-svg.js [--check] [--file diagrams/<slug>/<name>.html] [--out <dir>]';

const PAD = 16;   // matches the root padding the static template sets

const fail = cli.fail;

function renderFile(file, entry) {
  const source = fs.readFileSync(file, 'utf8');
  const parts = F.splitEmbed(source);
  if (!parts) fail(F.relPath(file) + ': missing embed markers');
  const frag = parts.fragment;
  const cls = F.rootClass(frag);
  if (!cls) fail(F.relPath(file) + ': missing root class');

  const styles = [...frag.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((m) => m[1]);
  const svgMatch = frag.match(/<svg\b([^>]*)>([\s\S]*?)<\/svg>/);
  if (!svgMatch) fail(F.relPath(file) + ': no <svg> in fragment');
  const attrs = svgMatch[1];
  const body = svgMatch[2];
  const vb = attrs.match(/viewBox="([\d.\s-]+)"/);
  if (!vb) fail(F.relPath(file) + ': <svg> has no viewBox');
  const [, , w, h] = vb[1].trim().split(/\s+/).map(Number);

  // The panel rect sits in an outer coordinate space that adds the padding
  // around the diagram's own viewBox; the body is translated into it, so
  // author coordinates stay valid. A nested <svg> would be simpler but the
  // panel-base rule sizes every svg to 100% width, which breaks the layout.
  const W = w + 2 * PAD, H = h + 2 * PAD;
  const label = (attrs.match(/aria-label="([^"]*)"/) || [, entry.title])[1];

  // Selectors are scoped under the root class, which the outer <svg> carries.
  // The panel radius is an attribute, not CSS rx, because image renderers do
  // not all honor rx as a property; the value is read from the palette block.
  const radius = (frag.match(/--radius:\s*(\d+)px/) || [, '12'])[1];
  const css = styles.join('\n')
    .replace(/<!--[\s\S]*?-->/g, '')
    .trim();
  const xlink = /\bxlink:/.test(body) ? ' xmlns:xlink="http://www.w3.org/1999/xlink"' : '';
  const out = xmlEntities([
    `<svg xmlns="http://www.w3.org/2000/svg"${xlink} viewBox="0 0 ${W} ${H}" class="fg-diagram ${cls}" role="img" aria-label="${escapeXml(decodeEntities(label), true)}">`,
    `<title>${escapeXml(entry.title)}</title>`,
    `<style>`,
    css,
    `.${cls} .fg-export-panel { fill: var(--bg); }`,
    `</style>`,
    `<rect class="fg-export-panel" width="${W}" height="${H}" rx="${radius}"/>`,
    `<g transform="translate(${PAD} ${PAD})">${body}</g>`,
    `</svg>`,
    '',
  ].join('\n'));
  const problem = wellFormed(out);
  if (problem) fail(F.relPath(file) + ': export is not well-formed XML: ' + problem);
  return out;
}

/* diagrams/<slug>/<name>.html -> <outDir>/<slug>/<name>.svg */
function exportPath(file, outDir) {
  return path.join(outDir, path.relative(F.DIAGRAMS_DIR, file).replace(/\.html$/, '.svg'));
}

function listSvgs(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? listSvgs(path.join(dir, e.name)) : e.name.endsWith('.svg') ? [path.join(dir, e.name)] : []);
}

function escapeXml(s, attr = false) {
  const t = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return attr ? t.replace(/"/g, '&quot;') : t;
}

/* HTML named entities that XML does not predefine, as numeric references.
   Unknown names are left alone so wellFormed() reports them. */
const HTML_ENTITIES = { nbsp: 160, hellip: 8230, rarr: 8594, larr: 8592, harr: 8596,
  mdash: 8212, ndash: 8211, times: 215, middot: 183, rsquo: 8217, lsquo: 8216,
  ldquo: 8220, rdquo: 8221, deg: 176, plusmn: 177, le: 8804, ge: 8805 };
const XML_ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" };

function xmlEntities(s) {
  return s.replace(/&([a-zA-Z]+);/g, (m, n) => (n in HTML_ENTITIES ? `&#${HTML_ENTITIES[n]};` : m));
}

function decodeEntities(s) {
  return s.replace(/&([a-zA-Z]+);/g, (m, n) =>
    n in XML_ENTITIES ? XML_ENTITIES[n] : n in HTML_ENTITIES ? String.fromCodePoint(HTML_ENTITIES[n]) : m);
}

/*
 * Minimal XML well-formedness check: balanced and properly nested tags,
 * quoted attributes, no bare '&' or '<'. Enough to catch what an HTML
 * fragment carries into an SVG image (void elements, HTML entities).
 * Returns a description of the first problem, or null.
 */
function wellFormed(xml) {
  const stack = [];
  const re = /<!--[\s\S]*?-->|<!\[CDATA\[[\s\S]*?\]\]>|<(\/?)([A-Za-z][\w:.-]*)((?:\s+[\w:.-]+\s*=\s*(?:"[^"<]*"|'[^'<]*'))*)\s*(\/?)>|<|&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)/g;
  let m, root = 0;
  while ((m = re.exec(xml)) !== null) {
    if (m[0] === '<') return `stray '<' at offset ${m.index}`;
    if (m[0] === '&' ) return `bare or unknown entity at offset ${m.index}: ${xml.slice(m.index, m.index + 12)}`;
    if (!m[2]) continue;
    if (m[1]) {
      const open = stack.pop();
      if (open !== m[2]) return `</${m[2]}> closes <${open}>`;
    } else if (!m[4]) {
      if (!stack.length && root++) return 'more than one root element';
      stack.push(m[2]);
    }
  }
  return stack.length ? `unclosed <${stack[stack.length - 1]}>` : null;
}

function main() {
  const { values } = cli.parse(USAGE, { check: { type: 'boolean' }, file: { type: 'string' }, out: { type: 'string' } });
  const check = !!values.check;
  const fileArg = values.file || null;
  if (check && (fileArg || values.out)) cli.usageError(USAGE, '--check compares the whole exports/ tree; it takes no --file or --out');
  const outDir = path.resolve(F.REPO_ROOT, values.out || 'exports');

  const byPath = new Map(F.loadManifest().map((e) => [e.path, e]));
  const files = fileArg ? [path.resolve(F.REPO_ROOT, fileArg)] : F.listDiagramFiles();
  const failures = [];
  const expected = new Set();
  let written = 0;
  for (const file of files) {
    const entry = byPath.get(F.relPath(file));
    if (!entry) fail(F.relPath(file) + ': not in manifest');
    if (entry.kind !== 'static') {
      if (fileArg) fail(F.relPath(file) + ': kind is not static; only static diagrams export');
      continue;
    }
    const out = renderFile(file, entry);
    const dest = exportPath(file, outDir);
    const rel = path.relative(F.REPO_ROOT, dest);
    expected.add(dest);
    if (check) {
      if (!fs.existsSync(dest)) failures.push(`${rel}: missing (run npm run export)`);
      else if (fs.readFileSync(dest, 'utf8') !== out) failures.push(`${rel}: differs from ${F.relPath(file)} (run npm run export)`);
    } else {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, out);
      console.log('[OK] ' + rel);
      written++;
    }
  }
  if (check) {
    // An export whose diagram was removed or is no longer static is stale too.
    for (const svg of listSvgs(outDir)) {
      if (!expected.has(svg)) failures.push(`${path.relative(F.REPO_ROOT, svg)}: no static diagram exports here (delete it)`);
    }
    report('export --check', failures, expected.size);
  }
  console.log(`export-svg: ${written} static diagram${written === 1 ? '' : 's'} written to ${path.relative(F.REPO_ROOT, outDir) || '.'}/`);
}

main();
