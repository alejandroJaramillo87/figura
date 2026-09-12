#!/usr/bin/env node
/*
 * export-svg.js — write each static diagram as a standalone SVG image.
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
 * still matches. Output is deterministic: a re-export after a diagram edit
 * is a reviewable diff for whichever repo committed the copy.
 *
 * Usage:
 *   node scripts/export-svg.js                    # every static diagram -> dist/
 *   node scripts/export-svg.js --file diagrams/<slug>/<name>.html
 *   node scripts/export-svg.js --out <dir>        # default: dist/
 */
'use strict';

const fs = require('fs');
const path = require('path');
const F = require('./lib/fragment');

const PAD = 16;   // matches the root padding the static template sets

function fail(msg) {
  console.error('[ERROR] ' + msg);
  process.exit(2);
}

function exportFile(file, entry, outDir) {
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
  const out = [
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" class="fg-diagram ${cls}" role="img" aria-label="${label}">`,
    `<title>${escapeXml(entry.title)}</title>`,
    `<style>`,
    css,
    `.${cls} .fg-export-panel { fill: var(--bg); }`,
    `</style>`,
    `<rect class="fg-export-panel" width="${W}" height="${H}" rx="${radius}"/>`,
    `<g transform="translate(${PAD} ${PAD})">${body}</g>`,
    `</svg>`,
    '',
  ].join('\n');

  const rel = path.relative(F.DIAGRAMS_DIR, file).replace(/\.html$/, '.svg');
  const dest = path.join(outDir, rel);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, out);
  console.log('[OK] ' + path.relative(F.REPO_ROOT, dest));
}

function escapeXml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function main() {
  const args = process.argv.slice(2);
  const fileArg = args.includes('--file') ? args[args.indexOf('--file') + 1] : null;
  const outDir = path.resolve(F.REPO_ROOT, args.includes('--out') ? args[args.indexOf('--out') + 1] : 'dist');

  const byPath = new Map(F.loadManifest().map((e) => [e.path, e]));
  const files = fileArg ? [path.resolve(F.REPO_ROOT, fileArg)] : F.listDiagramFiles();
  let n = 0;
  for (const file of files) {
    const entry = byPath.get(F.relPath(file));
    if (!entry) fail(F.relPath(file) + ': not in manifest');
    if (entry.kind !== 'static') {
      if (fileArg) fail(F.relPath(file) + ': kind is not static; only static diagrams export');
      continue;
    }
    exportFile(file, entry, outDir);
    n++;
  }
  console.log(`export-svg: ${n} static diagram${n === 1 ? '' : 's'} written to ${path.relative(F.REPO_ROOT, outDir) || '.'}/`);
}

main();
