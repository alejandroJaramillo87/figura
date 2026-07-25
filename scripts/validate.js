#!/usr/bin/env node
/*
 * validate.js — contract linter for the CLAUDE.md hard rules.
 *
 * Checks every diagram fragment for: embed markers, root-class CSS scoping,
 * prefixed keyframes and SVG ids, scoped JS conventions, self-containment
 * (no external URLs, imports, or absolute paths), reduced-motion coverage,
 * SMIL comet gating, accessibility attributes, and manifest consistency.
 *
 * Usage:
 *   node scripts/validate.js           # strict: exit 1 on any finding
 *   node scripts/validate.js --warn    # report only, always exit 0
 */
'use strict';

const fs = require('fs');
const path = require('path');
const F = require('./lib/fragment');

/* per-file rule exemptions (currently none) */
const EXEMPT = {};

const findings = [];
function report(file, rule, msg) {
  const rel = file ? F.relPath(file) : '(repo)';
  if (file && (EXEMPT[rel] || []).includes(rule)) return;
  findings.push({ rel, rule, msg });
}

/* --- CSS checks ---------------------------------------------------------- */

function stripCssComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, '');
}

/* Collect top-level selector lists from a CSS string (recursing into @media). */
function collectSelectors(css, out) {
  let i = 0;
  while (i < css.length) {
    const brace = css.indexOf('{', i);
    if (brace === -1) break;
    const head = css.slice(i, brace).trim();
    if (head.startsWith('@media')) {
      // find matching closing brace of the media block
      let depth = 1, j = brace + 1;
      while (j < css.length && depth > 0) {
        if (css[j] === '{') depth++;
        else if (css[j] === '}') depth--;
        j++;
      }
      collectSelectors(css.slice(brace + 1, j - 1), out);
      i = j;
    } else if (head.startsWith('@keyframes')) {
      out.keyframes.push(head.replace('@keyframes', '').trim());
      let depth = 1, j = brace + 1;
      while (j < css.length && depth > 0) {
        if (css[j] === '{') depth++;
        else if (css[j] === '}') depth--;
        j++;
      }
      i = j;
    } else if (head.startsWith('@')) {
      // other at-rules (@import etc.) — flagged separately
      i = css.indexOf('}', brace) + 1 || css.length;
    } else {
      if (head) out.selectors.push(head);
      let depth = 1, j = brace + 1;
      while (j < css.length && depth > 0) {
        if (css[j] === '{') depth++;
        else if (css[j] === '}') depth--;
        j++;
      }
      i = j;
    }
  }
}

/* The closed set of sprite-ramp tokens (declared in shared/tokens.css) —
   a var(--px-*) reference outside this set resolves to nothing at render
   time, so a typo'd or invented ramp token fails silently. */
const PX_TOKENS = (() => {
  const css = fs.readFileSync(path.join(F.REPO_ROOT, 'shared', 'tokens.css'), 'utf8');
  return new Set([...css.matchAll(/--fg-(px-[a-z0-9-]+)\s*:/g)].map((m) => m[1]));
})();

/* --- hero checks: generator/template class sync + settled completeness --- */

function checkHero(file, frag, cls) {
  if (frag.includes('@SPRITES@')) {
    report(file, 'hero-sprites', 'unsubstituted @SPRITES@ marker (generator not run?)');
  }

  /* classes attached to SVG elements by the generator */
  const svg = (frag.match(/<svg\b[\s\S]*?<\/svg>/) || [''])[0];
  const markupClasses = new Set();
  for (const m of svg.matchAll(/class="([^"]+)"/g)) {
    for (const c of m[1].split(/\s+/)) if (c) markupClasses.add(c);
  }

  /* classes the template's CSS selects */
  const styles = [...frag.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((m) => m[1]);
  const rawCss = styles.join('\n');
  const exempt = new Set(
    [...rawCss.matchAll(/fg:settled-exempt\s+([a-zA-Z0-9_-]+)/g)].map((m) => m[1]));
  /* structural grouping classes with no CSS of their own (variants carry
     the rules) are declared via fg:sync-exempt in a template comment */
  const syncExempt = new Set(
    [...rawCss.matchAll(/fg:sync-exempt\s+([a-zA-Z0-9_ -]+)/g)]
      .flatMap((m) => m[1].trim().split(/\s+/)));
  const out = { selectors: [], keyframes: [] };
  for (const s of styles) collectSelectors(stripCssComments(s), out);
  const STATE = new Set(['is-live', 'is-settled', 'is-paused', 'fg-diagram', cls]);
  const cssClasses = new Set();
  const liveClasses = new Set();
  const settledClasses = new Set();
  for (const selList of out.selectors) {
    for (const sel of selList.split(',')) {
      const classes = [...sel.matchAll(/\.([a-zA-Z0-9_-]+)/g)]
        .map((m) => m[1]).filter((c) => !STATE.has(c));
      for (const c of classes) cssClasses.add(c);
      if (sel.includes('.is-live')) for (const c of classes) liveClasses.add(c);
      if (sel.includes('.is-settled')) for (const c of classes) settledClasses.add(c);
    }
  }

  /* symmetric generator <-> template sync */
  for (const c of markupClasses) {
    if (!cssClasses.has(c) && !syncExempt.has(c)) {
      report(file, 'hero-sync', `SVG class "${c}" has no CSS rule (generator/template drift)`);
    }
  }
  for (const c of cssClasses) {
    if (!markupClasses.has(c)) {
      report(file, 'hero-sync', `CSS class ".${c}" not attached to any SVG element (generator/template drift)`);
    }
  }

  /* the settled state is the reduced-motion rendering — it must cover
     every class the intro animates */
  for (const c of liveClasses) {
    if (!settledClasses.has(c) && !exempt.has(c)) {
      report(file, 'hero-settled',
        `class "${c}" animated under .is-live has no .is-settled rule ` +
        '(add one, or mark intro-only via /* fg:settled-exempt ' + c + ' */)');
    }
  }
}

function checkFile(file, kind) {
  const source = fs.readFileSync(file, 'utf8');
  const rel = F.relPath(file);

  if (/(?:src|href)="(?:file:)?\/(?!\/)/.test(source) || /url\(\s*['"]?\//.test(source)) {
    report(file, 'absolute-path', 'absolute path reference in file');
  }

  const parts = F.splitEmbed(source);
  if (!parts) {
    report(file, 'embed-markers', 'missing or unbalanced fg:embed markers');
    return;
  }
  const frag = parts.fragment;

  const cls = F.rootClass(frag);
  if (!cls) {
    report(file, 'root-class', 'root element must carry class="fg-diagram fg-<name>"');
    return;
  }

  /* self-containment */
  if (/<link\b/i.test(frag)) report(file, 'self-contained', '<link> inside fragment');
  if (/@import/.test(frag)) report(file, 'self-contained', '@import inside fragment');
  if (/<script[^>]+src=/i.test(frag)) report(file, 'self-contained', 'external <script src> inside fragment');
  const urlRefs = frag.match(/(?:src|href|xlink:href)\s*=\s*"(https?:)?\/\/[^"]*"/gi) || [];
  for (const u of urlRefs) {
    if (!u.includes('www.w3.org')) report(file, 'self-contained', `external URL ref: ${u}`);
  }
  if (/url\(\s*['"]?https?:/i.test(frag)) report(file, 'self-contained', 'external url() in CSS');

  /* CSS scoping */
  const styles = [...frag.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((m) => m[1]);
  const out = { selectors: [], keyframes: [] };
  for (const s of styles) collectSelectors(stripCssComments(s), out);
  for (const selList of out.selectors) {
    for (const sel of selList.split(',').map((s) => s.trim()).filter(Boolean)) {
      // keyframe stop selectors (from/to/%) reach here only if nested parse missed; allow
      if (/^(from|to|\d+%)/.test(sel)) continue;
      if (!sel.startsWith('.' + cls)) {
        report(file, 'css-scope', `selector not scoped under .${cls}: "${sel}"`);
      }
    }
  }
  for (const kf of out.keyframes) {
    if (!/^fg-[a-z0-9]+-/.test(kf)) report(file, 'keyframes', `keyframe name not fg-<abbr>-* prefixed: "${kf}"`);
  }

  /* motion tokens: easing curves and dim state fills come from the palette
     block, never hand-written — a tokens.css change must reach every state */
  {
    let unmanaged = frag;
    for (const b of F.findBlocks(frag).slice().reverse()) {
      unmanaged = unmanaged.slice(0, b.start) + unmanaged.slice(b.end);
    }
    if (/cubic-bezier\(/.test(unmanaged)) {
      report(file, 'motion-token', 'literal cubic-bezier() outside managed blocks (use var(--ease))');
    }
    const dimHexes = unmanaged.match(/#(?:0c3550|12283f|0e4429|14352a|123c2e|4a3608|4a1d1d|3f1d1d|2a2350)\b/gi) || [];
    for (const h of dimHexes) {
      report(file, 'dim-token', `hand-mixed dim state fill ${h} (use var(--accent-dim)/--ok-dim/--warn-dim/--hot-dim/--violet-dim)`);
    }
    for (const m of unmanaged.matchAll(/var\(--(px-[a-z0-9-]+)/g)) {
      if (!PX_TOKENS.has(m[1])) {
        report(file, 'px-token', `unknown sprite-ramp token var(--${m[1]}) (the --px-* set in shared/tokens.css is closed)`);
      }
    }
  }

  if (kind === 'hero') checkHero(file, frag, cls);

  /* reduced motion */
  if (!frag.includes('prefers-reduced-motion')) {
    report(file, 'reduced-motion', 'no prefers-reduced-motion handling in fragment');
  }
  if (frag.includes('<animateMotion')) {
    const media = [...frag.matchAll(/@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([\s\S]*?)\n\}/g)];
    const gated = media.some((m) => /display:\s*none/.test(m[1]));
    if (!gated) report(file, 'smil-gate', '<animateMotion> present but no display:none reduced-motion gate');
  }

  /* SVG ids: prefixed and consistent within the file */
  const ids = [...frag.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]);
  for (const id of ids) {
    if (!/^[a-z0-9]+-/.test(id)) report(file, 'id-prefix', `SVG id not diagram-prefixed: "${id}"`);
  }
  /* id refs resolve within the fragment */
  const refs = [...frag.matchAll(/(?:url\(#|href="#|begin=")([a-zA-Z0-9-]+)/g)].map((m) => m[1]);
  for (const r of refs) {
    const base = r.split('.')[0]; // syncbase refs like xx-head.begin+0.1s
    if (base === 'indefinite') continue;
    if (/^-?[\d.]+s?$/.test(base) || /^-?\d/.test(base)) continue; // begin="-2.1s" time offsets
    if (!ids.includes(base)) report(file, 'id-ref', `reference to undefined id: "${base}"`);
  }

  /* accessibility */
  const svgTags = [...frag.matchAll(/<svg\b[^>]*>/g)].map((m) => m[0]);
  for (const tag of svgTags) {
    if (!tag.includes('role="img"')) report(file, 'a11y', '<svg> missing role="img"');
    if (!tag.includes('aria-label=')) report(file, 'a11y', '<svg> missing aria-label');
  }

  /* JS conventions */
  const scripts = [...frag.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  for (const js of scripts) {
    if (!js.includes("document.currentScript.closest('.fg-diagram')")) {
      report(file, 'js-scope', 'script does not resolve root via document.currentScript.closest');
    }
    if (js.includes('getElementById')) report(file, 'js-scope', 'getElementById used (query within root instead)');
    if (js.includes('DOMContentLoaded')) report(file, 'js-scope', 'DOMContentLoaded used (script sits after markup)');
    try {
      new Function(js);   // parse only: catches syntax errors and duplicate declarations
    } catch (e) {
      report(file, 'js-syntax', `script does not parse: ${e.message}`);
    }
  }
}

/* --- manifest checks ----------------------------------------------------- */

function checkManifest(files) {
  let manifest;
  try {
    manifest = F.loadManifest();
  } catch (e) {
    report(null, 'manifest', `manifest.json unreadable: ${e.message}`);
    return;
  }
  const KINDS = ['step-timeline', 'hover-inspect', 'ambient', 'hero'];
  const rels = new Set(files.map((f) => F.relPath(f)));
  const seenIds = new Set();
  const seenPaths = new Set();
  for (const entry of manifest) {
    for (const k of ['id', 'path', 'title', 'post', 'description']) {
      if (!(k in entry)) report(null, 'manifest', `entry "${entry.id || entry.path}" missing field "${k}"`);
    }
    if ('kind' in entry && !KINDS.includes(entry.kind)) {
      report(null, 'manifest', `entry "${entry.id}" has unknown kind "${entry.kind}"`);
    }
    if (seenIds.has(entry.id)) report(null, 'manifest', `duplicate id "${entry.id}"`);
    if (seenPaths.has(entry.path)) report(null, 'manifest', `duplicate path "${entry.path}"`);
    seenIds.add(entry.id);
    seenPaths.add(entry.path);
    if (!rels.has(entry.path)) {
      report(null, 'manifest', `path does not exist: ${entry.path}`);
    } else {
      rels.delete(entry.path);
    }
    const stem = path.basename(entry.path || '', '.html');
    if (entry.id !== stem) report(null, 'manifest-id', `id "${entry.id}" != filename stem "${stem}"`);
  }
  for (const orphan of rels) report(null, 'manifest', `diagram not in manifest: ${orphan}`);
}

function main() {
  const warnOnly = process.argv.includes('--warn');
  const files = F.listDiagramFiles();
  let kinds = new Map();
  try {
    kinds = new Map(F.loadManifest().map((e) => [e.path, e.kind]));
  } catch (e) { /* unreadable manifest is reported by checkManifest */ }
  for (const f of files) checkFile(f, kinds.get(F.relPath(f)));
  checkManifest(files);

  for (const f of findings) console.error(`[${warnOnly ? 'WARN' : 'FAIL'}] ${f.rel} (${f.rule}): ${f.msg}`);
  const byRule = {};
  for (const f of findings) byRule[f.rule] = (byRule[f.rule] || 0) + 1;
  console.error(`validate: ${files.length} files, ${findings.length} findings` +
    (findings.length ? ` (${Object.entries(byRule).map(([k, v]) => `${k}: ${v}`).join(', ')})` : ''));
  process.exit(warnOnly || !findings.length ? 0 : 1);
}

main();
