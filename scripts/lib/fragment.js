/*
 * fragment.js — shared parsing helpers for the figura build/validate scripts.
 *
 * A diagram file contains one embed fragment between the markers
 * <!-- fg:embed-start --> and <!-- fg:embed-end -->. Inside the fragment,
 * managed blocks are delimited by sentinel comments:
 *
 *   CSS:  /* fg:begin <name> v<N> *\/ ... /* fg:end <name> *\/
 *   JS:   // fg:begin <name> v<N>  ...  // fg:end <name>
 *
 * Block contents are owned by scripts/build.js, which re-expands them from
 * shared/runtime/ (and the palettes from shared/tokens.css). Everything
 * outside the sentinels is diagram-specific and never touched.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..', '..');
const DIAGRAMS_DIR = path.join(REPO_ROOT, 'diagrams');
const RUNTIME_DIR = path.join(REPO_ROOT, 'shared', 'runtime');
const TOKENS_PATH = path.join(REPO_ROOT, 'shared', 'tokens.css');
const MANIFEST_PATH = path.join(REPO_ROOT, 'manifest.json');

const EMBED_START = '<!-- fg:embed-start -->';
const EMBED_END = '<!-- fg:embed-end -->';

/* Matches one managed block, CSS or JS style, capturing name/version/body. */
const BLOCK_RE =
  /(\/\* fg:begin ([a-z0-9-]+) v(\d+) \*\/|\/\/ fg:begin ([a-z0-9-]+) v(\d+))\n([\s\S]*?)(\/\* fg:end \2? ?\*\/|\/\/ fg:end \4?)/g;

function listDiagramFiles() {
  const out = [];
  for (const slug of fs.readdirSync(DIAGRAMS_DIR).sort()) {
    const dir = path.join(DIAGRAMS_DIR, slug);
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const f of fs.readdirSync(dir).sort()) {
      if (f.endsWith('.html')) out.push(path.join(dir, f));
    }
  }
  return out;
}

function relPath(file) {
  return path.relative(REPO_ROOT, file);
}

/* Extract the embed fragment; returns { before, fragment, after } or null. */
function splitEmbed(source) {
  const s = source.indexOf(EMBED_START);
  const e = source.indexOf(EMBED_END);
  if (s === -1 || e === -1 || e < s) return null;
  const fragStart = s + EMBED_START.length;
  return {
    before: source.slice(0, fragStart),
    fragment: source.slice(fragStart, e),
    after: source.slice(e),
  };
}

/* Root class of the fragment, e.g. "fg-kv-cache-fill". */
function rootClass(fragment) {
  const m = fragment.match(/class="fg-diagram (fg-[a-z0-9-]+)(?:[" ])/);
  return m ? m[1] : null;
}

/* Find managed blocks in a string: [{ name, version, body, start, end, style }] */
function findBlocks(text) {
  const blocks = [];
  let m;
  BLOCK_RE.lastIndex = 0;
  while ((m = BLOCK_RE.exec(text)) !== null) {
    const style = m[2] ? 'css' : 'js';
    blocks.push({
      name: m[2] || m[4],
      version: Number(m[3] || m[5]),
      body: m[6],
      start: m.index,
      end: m.index + m[0].length,
      full: m[0],
      style,
    });
  }
  return blocks;
}

function beginMarker(name, version, style) {
  return style === 'css' ? `/* fg:begin ${name} v${version} */` : `// fg:begin ${name} v${version}`;
}

function endMarker(name, style) {
  return style === 'css' ? `/* fg:end ${name} */` : `// fg:end ${name}`;
}

function renderBlock(name, version, style, body) {
  return `${beginMarker(name, version, style)}\n${body}${endMarker(name, style)}`;
}

/* --- palette generation from tokens.css --------------------------------- */

/* Local (unprefixed) names diagrams use, mapped from the tokens.css names. */
const PALETTE_PREFIX = { 'palette-classic': '--fg-' };

function parseTokens() {
  const css = fs.readFileSync(TOKENS_PATH, 'utf8');
  const vars = [];
  const re = /(--fg-[a-z0-9-]+)\s*:\s*([^;]+);/g;
  let m;
  while ((m = re.exec(css)) !== null) vars.push([m[1], m[2].trim()]);
  return vars;
}

/* Render a palette block body: one rule declaring local var names on SCOPE. */
function renderPalette(name, scope) {
  const prefix = PALETTE_PREFIX[name];
  const lines = parseTokens().map(([k, v]) => `  --${k.slice(prefix.length)}: ${v};`);
  return `${scope} {\n${lines.join('\n')}\n}\n`;
}

/* Resolve the canonical body for a managed block name.
   rootCls is the root class without the leading dot, e.g. "fg-kv-cache-fill". */
function canonicalBody(name, rootCls) {
  const scope = '.' + rootCls;
  if (PALETTE_PREFIX[name]) return renderPalette(name, scope);
  for (const ext of ['css', 'js']) {
    const p = path.join(RUNTIME_DIR, `${name}.${ext}`);
    if (fs.existsSync(p)) return fs.readFileSync(p, 'utf8').replaceAll('{{SCOPE}}', scope);
  }
  return null;
}

function loadManifest() {
  return JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
}

module.exports = {
  REPO_ROOT, DIAGRAMS_DIR, RUNTIME_DIR, MANIFEST_PATH,
  EMBED_START, EMBED_END, PALETTE_PREFIX,
  listDiagramFiles, relPath, splitEmbed, rootClass,
  findBlocks, renderBlock, beginMarker, endMarker,
  renderPalette, canonicalBody, loadManifest,
};
