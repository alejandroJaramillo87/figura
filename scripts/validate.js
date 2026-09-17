#!/usr/bin/env node
/*
 * validate.js — contract linter for the CLAUDE.md hard rules.
 *
 * Checks every diagram fragment for: embed markers, root-class CSS scoping,
 * prefixed keyframes and SVG ids, scoped JS conventions, self-containment
 * (no external URLs, imports, or absolute paths), reduced-motion coverage,
 * SMIL comet gating, accessibility attributes, and manifest consistency.
 * Diagrams the manifest marks kind "static" additionally carry no script,
 * no SMIL, no CSS motion, and no controls or caption chrome, so that the
 * fragment can be exported as a standalone SVG (scripts/export-svg.js).
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

  /* the fragment with managed blocks removed: rules about what an author may
     write apply only to the diagram-specific parts */
  let unmanaged = frag;
  for (const b of F.findBlocks(frag).slice().reverse()) {
    unmanaged = unmanaged.slice(0, b.start) + unmanaged.slice(b.end);
  }

  /* motion tokens: easing curves and dim state fills come from the palette
     block, never hand-written — a tokens.css change must reach every state */
  {
    if (/cubic-bezier\(/.test(unmanaged)) {
      report(file, 'motion-token', 'literal cubic-bezier() outside managed blocks (use var(--ease))');
    }
    const dimHexes = unmanaged.match(/#(?:0c3550|12283f|0e4429|14352a|123c2e|4a3608|4a1d1d|3f1d1d|2a2350)\b/gi) || [];
    for (const h of dimHexes) {
      report(file, 'dim-token', `hand-mixed dim state fill ${h} (use var(--accent-dim)/--ok-dim/--warn-dim/--hot-dim/--violet-dim)`);
    }
  }

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

  /* static kind: nothing that needs a script engine or a clock, so the
     fragment survives export to a standalone SVG consumed as an image */
  if (kind === 'static') {
    if (scripts.length) report(file, 'static-script', 'static diagram contains a <script>');
    if (/<(?:animate|animateMotion|animateTransform|set)\b/.test(frag)) {
      report(file, 'static-smil', 'static diagram contains a SMIL animation element');
    }
    if (out.keyframes.length) report(file, 'static-motion', 'static diagram declares @keyframes');
    if (/(?:^|[\s;{])(?:animation|transition)(?:-[a-z]+)?\s*:/.test(stripCssComments(unmanaged))) {
      report(file, 'static-motion', 'animation or transition declaration outside managed blocks');
    }
    if (/class="[^"]*\bfg-(?:controls|caption)\b/.test(frag)) {
      report(file, 'static-chrome', 'static diagram carries .fg-controls or .fg-caption markup');
    }
  }
}

/* --- manifest checks ----------------------------------------------------- */

const KINDS = ['step-timeline', 'hover-inspect', 'ambient', 'static'];

function checkManifest(manifest, files) {
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
  let manifest = null;
  try {
    manifest = F.loadManifest();
  } catch (e) {
    report(null, 'manifest', `manifest.json unreadable: ${e.message}`);
  }
  const kindOf = new Map((manifest || []).map((e) => [e.path, e.kind]));
  for (const f of files) checkFile(f, kindOf.get(F.relPath(f)));
  if (manifest) checkManifest(manifest, files);

  for (const f of findings) console.error(`[${warnOnly ? 'WARN' : 'FAIL'}] ${f.rel} (${f.rule}): ${f.msg}`);
  const byRule = {};
  for (const f of findings) byRule[f.rule] = (byRule[f.rule] || 0) + 1;
  console.error(`validate: ${files.length} files, ${findings.length} findings` +
    (findings.length ? ` (${Object.entries(byRule).map(([k, v]) => `${k}: ${v}`).join(', ')})` : ''));
  process.exit(warnOnly || !findings.length ? 0 : 1);
}

main();
