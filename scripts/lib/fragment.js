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

/* One sentinel token, CSS or JS style. A begin carries a version; an end does not. */
const TOKEN_RE =
  /\/\* fg:(begin|end) ([a-z0-9-]+)(?: v(\d+))? \*\/|\/\/ fg:(begin|end) ([a-z0-9-]+)(?: v(\d+))?(?=\r?\n|$)/g;
/* Any text that looks like a sentinel, well formed or not. */
const LOOSE_RE = /fg:(?:begin|end)\b/g;

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

/*
 * Find managed blocks in a string: [{ name, version, body, start, end, style }].
 *
 * Every begin must be closed by an end of the same name and comment style
 * before any other sentinel appears; nesting, an orphan end, an unclosed
 * begin, or text that mentions fg:begin/fg:end without forming a valid
 * sentinel is an error. A lenient match here once let a malformed end marker
 * swallow the rest of a diagram, which build.js then overwrote.
 * Throws an Error whose message names the first problem.
 */
function findBlocks(text) {
  const tokens = [];
  let m;
  TOKEN_RE.lastIndex = 0;
  while ((m = TOKEN_RE.exec(text)) !== null) {
    const css = m[1] !== undefined;
    tokens.push({
      kind: css ? m[1] : m[4],
      name: css ? m[2] : m[5],
      version: css ? m[3] : m[6],
      style: css ? 'css' : 'js',
      start: m.index,
      end: m.index + m[0].length,
    });
  }
  const loose = (text.match(LOOSE_RE) || []).length;
  if (loose !== tokens.length) {
    throw new Error(`${loose - tokens.length} malformed fg:begin/fg:end sentinel(s)`);
  }

  const blocks = [];
  for (let i = 0; i < tokens.length; i += 2) {
    const b = tokens[i], e = tokens[i + 1];
    if (b.kind !== 'begin') throw new Error(`fg:end ${b.name} without a matching fg:begin`);
    if (b.version === undefined) throw new Error(`fg:begin ${b.name} has no version`);
    if (!e) throw new Error(`fg:begin ${b.name} is never closed`);
    if (e.kind !== 'end') throw new Error(`fg:begin ${e.name} nested inside ${b.name}`);
    if (e.version !== undefined) throw new Error(`fg:end ${e.name} carries a version`);
    if (e.name !== b.name || e.style !== b.style) {
      throw new Error(`fg:begin ${b.name} closed by fg:end ${e.name} (${e.style})`);
    }
    const nl = text.slice(b.end).match(/^\r?\n/);
    if (!nl) throw new Error(`fg:begin ${b.name} is not followed by a newline`);
    blocks.push({
      name: b.name,
      version: Number(b.version),
      body: text.slice(b.end + nl[0].length, e.start),
      start: b.start,
      end: e.end,
      full: text.slice(b.start, e.end),
      style: b.style,
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
  REPO_ROOT, DIAGRAMS_DIR, MANIFEST_PATH,
  listDiagramFiles, relPath, splitEmbed, rootClass,
  findBlocks, renderBlock, canonicalBody, loadManifest,
};
