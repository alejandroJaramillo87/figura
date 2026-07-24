#!/usr/bin/env node
/*
 * migrate.js — one-off: wrap hand-copied boilerplate in managed blocks.
 *
 * Recognizes the recurring shapes (palette var rule, panel base, controls
 * bar, caption box, reduced-motion kill, inline timeline JS) with tolerant
 * regexes and replaces them with fg:begin/fg:end sentinel blocks whose
 * contents come from the canonical sources. Everything unrecognized is
 * preserved byte-for-byte; files it cannot confidently match are reported
 * for manual treatment. Delete this script once migration is complete.
 *
 * Usage: node scripts/migrate.js [--dry] [--file <path>]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const F = require('./lib/fragment');

const dry = process.argv.includes('--dry');
const fileArg = process.argv.includes('--file')
  ? process.argv[process.argv.indexOf('--file') + 1] : null;

/* Canonical palette values (local names) per palette, from tokens.css. */
function paletteMap(name) {
  const body = F.renderPalette(name, 'x');
  const map = {};
  for (const m of body.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;]+);/g)) map[m[1]] = m[2].trim();
  return map;
}
const PALETTES = {
  'palette-classic': paletteMap('palette-classic'),
  'palette-pastel-dark': paletteMap('palette-pastel-dark'),
  'palette-pastel-light': paletteMap('palette-pastel-light'),
};

function detectPalette(decls) {
  const has = (k) => decls.some(([n]) => n === k);
  const val = (k) => (decls.find(([n]) => n === k) || [])[1];
  if (has('--mint-fill') || val('--bg') === '#fdfbf7') return 'palette-pastel-light';
  if (has('--mint') || has('--lavender')) return 'palette-pastel-dark';
  return 'palette-classic';
}

/* Split a declaration body "a: b; c: d;" into [[name, value], ...],
   dropping comments. Returns null if it contains nested braces. */
function splitDecls(body) {
  if (body.includes('{')) return null;
  const clean = body.replace(/\/\*[\s\S]*?\*\//g, '');
  const out = [];
  for (const part of clean.split(';')) {
    const p = part.trim();
    if (!p) continue;
    const i = p.indexOf(':');
    if (i === -1) return null;
    out.push([p.slice(0, i).trim(), p.slice(i + 1).trim()]);
  }
  return out;
}

const PANEL_PROPS = {
  'background': 'var(--bg)',
  'border-radius': '12px',
  'font-family': '"Work Sans", system-ui, -apple-system, "Segoe UI", sans-serif',
  'line-height': '1.4',
  'box-shadow': '0 4px 20px rgba(0, 0, 0, 0.3)',
};
const PANEL_LIGHT_PROPS = {
  'background': 'var(--bg)',
  'border': '1px solid var(--border)',
  'border-radius': '12px',
  'font-family': '"Work Sans", system-ui, -apple-system, "Segoe UI", sans-serif',
  'line-height': '1.4',
  'box-shadow': '0 2px 12px rgba(120, 100, 60, 0.10)',
};

const skipped = [];   // [file, what, why]

function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

/* ---- CSS: first root rule → palette + panel-base + residual ---- */
function migrateRootRule(frag, cls, notes) {
  const re = new RegExp(`(<style>\\n)(\\.${esc(cls)}\\s*\\{([^}]*)\\})`);
  const m = frag.match(re);
  if (!m) { skipped.push([cls, 'root-rule', 'first rule not found directly after <style>']); return frag; }
  const decls = splitDecls(m[3]);
  if (!decls) { skipped.push([cls, 'root-rule', 'could not parse declarations']); return frag; }

  const palName = detectPalette(decls);
  const pal = PALETTES[palName];
  const light = palName === 'palette-pastel-light';
  const panelProps = light ? PANEL_LIGHT_PROPS : PANEL_PROPS;

  const residual = [];
  for (const [n, v] of decls) {
    if (n.startsWith('--')) {
      if (pal[n] === v) continue;               // covered by palette block
      residual.push([n, v]);                    // custom or overridden var
    } else if (panelProps[n] === v) {
      continue;                                 // covered by panel block
    } else {
      residual.push([n, v]);                    // padding, custom props
    }
  }

  const scope = '.' + cls;
  const palBlock = F.renderBlock(palName, 1, 'css', F.canonicalBody(palName, cls));
  const panelBlock = F.renderBlock(light ? 'panel-base-light' : 'panel-base', 1, 'css',
    F.canonicalBody(light ? 'panel-base-light' : 'panel-base', cls));
  let residualRule = '';
  if (residual.length) {
    residualRule = `${scope} {\n${residual.map(([n, v]) => `  ${n}: ${v};`).join('\n')}\n}\n`;
  }
  notes.palette = palName;

  /* svg/text base rules immediately after the root rule are part of panel-base */
  let rest = frag.slice(frag.indexOf(m[2]) + m[2].length);
  const svgRe = new RegExp(`^\\n\\.${esc(cls)} svg \\{ display: block; width: 100%; height: auto; \\}\\n\\.${esc(cls)} text \\{ font-family: inherit; \\}\\n`);
  if (svgRe.test(rest)) {
    rest = rest.replace(svgRe, '\n');
  } else {
    skipped.push([cls, 'svg-text-base', 'svg/text base rules not in canonical shape; left in place']);
  }

  return frag.slice(0, m.index) + m[1] + palBlock + '\n' + panelBlock + '\n' + residualRule + rest;
}

/* ---- CSS: controls bar ---- */
function migrateControls(frag, cls, notes) {
  const scope = esc('.' + cls);
  const re = new RegExp(
    `\\.${esc(cls)} \\.fg-controls \\{[^}]*\\}\\n` +
    `\\.${esc(cls)} \\.fg-controls button \\{([^}]*)\\}\\n` +
    `\\.${esc(cls)} \\.fg-controls button:hover \\{ border-color: var\\((--[a-z-]+)\\); \\}\\n` +
    `\\.${esc(cls)} \\.fg-controls \\[data-fg="counter"\\] \\{[^}]*\\}\\n`
  );
  const m = frag.match(re);
  if (!m) return frag;
  if (!m[1].includes('width: 34px')) return frag;   // text-pill variant: leave custom
  const accent = m[2];
  const block = F.renderBlock('controls-bar', 1, 'css', F.canonicalBody('controls-bar', cls));
  let extra = '';
  if (accent !== '--accent') extra = `.${cls} { --fg-ctl-accent: var(${accent}); }\n`;
  notes.controls = true;
  return frag.replace(re, block + '\n' + extra);
}

/* ---- CSS: caption box ---- */
function migrateCaption(frag, cls, notes) {
  const re = new RegExp(`\\.${esc(cls)} \\.fg-caption \\{([^}]*)\\}\\n`);
  const m = frag.match(re);
  if (!m) return frag;
  const decls = splitDecls(m[1]);
  if (!decls) return frag;
  const canonical = {
    'margin-top': '12px', 'padding': '10px 14px', 'background': 'var(--panel)',
    'border-radius': '0 8px 8px 0', 'color': 'var(--text)', 'font-size': '13px',
  };
  const extras = [];
  for (const [n, v] of decls) {
    if (canonical[n] === v) continue;
    if (n === 'border-left') {
      const am = v.match(/^3px solid var\((--[a-z-]+)\)$/);
      if (am) { if (am[1] !== '--accent') extras.push(['--fg-cap-accent', `var(${am[1]})`]); continue; }
      return frag;                                   // unusual border: leave custom
    }
    if (n === 'min-height') {
      if (v !== '4.2em') extras.push(['--fg-cap-minh', v]);
      continue;
    }
    return frag;                                     // extra property: leave custom
  }
  const block = F.renderBlock('caption-box', 1, 'css', F.canonicalBody('caption-box', cls));
  let extra = '';
  if (extras.length) extra = `.${cls} {\n${extras.map(([n, v]) => `  ${n}: ${v};`).join('\n')}\n}\n`;
  notes.caption = true;
  return frag.replace(re, block + '\n' + extra);
}

/* ---- CSS: reduced-motion kill ---- */
function migrateReducedMotion(frag, cls, notes) {
  const re = /@media \(prefers-reduced-motion: reduce\) \{\n([\s\S]*?)\n\}\n/;
  const m = frag.match(re);
  if (!m) return frag;
  const inner = m[1];
  // split inner into rules; classify kill rules (only transition/animation: none)
  const rules = [...inner.matchAll(/([^{}]+)\{([^}]*)\}/g)];
  const keep = [];
  for (const r of rules) {
    const decls = splitDecls(r[2]);
    if (!decls) { skipped.push([cls, 'reduced-motion', 'nested/unparsable media rules']); return frag; }
    const isKill = decls.every(([n, v]) =>
      (n === 'transition' || n === 'animation') && v.replace(' !important', '') === 'none');
    if (!isKill) keep.push(`  ${r[1].trim()} { ${r[2].trim()} }`);
  }
  const block = F.renderBlock('reduced-motion', 1, 'css', F.canonicalBody('reduced-motion', cls));
  let keepBlock = '';
  if (keep.length) {
    keepBlock = `@media (prefers-reduced-motion: reduce) {\n${keep.join('\n')}\n}\n`;
  }
  notes.reduced = true;
  return frag.replace(re, block + '\n' + keepBlock);
}

/* ---- JS: timeline core + start ---- */
function migrateTimeline(frag, cls, notes) {
  if (!/let step = 0, timer = null;/.test(frag)) return frag;

  const coreRe = /let step = 0, timer = null;\n\n {2}function apply\(\) \{\n(?:.*\n)*? {2}\}\n {2}const tl = \{\n(?:.*\n)*? {2}\};\n\n {2}const btn = [\s\S]*?root\.querySelectorAll\('\.fg-controls button'\)\.forEach\(\(b\) => b\.addEventListener\('click', sync\)\);\n/;
  const m = frag.match(coreRe);
  if (!m) { skipped.push([cls, 'timeline-core', 'timeline present but shape not recognized']); return frag; }

  // insert unindented; scripts/build.js re-indents bodies to the marker indent
  const coreBlock = F.renderBlock('timeline-core', 1, 'js', F.canonicalBody('timeline-core', cls));
  frag = frag.replace(coreRe, coreBlock + '\n');

  // drop a now-duplicate `const reduced = ...` line (the block defines it)
  frag = frag.replace(/\n {2}const reduced = window\.matchMedia\('\(prefers-reduced-motion: reduce\)'\)\.matches;\n/, '\n');

  // start tail: apply() + reduced/autoplay branches (two variants)
  const startReA = / {2}apply\(\);\n\n {2}if \(window\.matchMedia\('\(prefers-reduced-motion: reduce\)'\)\.matches\) \{\n[\s\S]*?\n {2}\} else \{\n {4}const io = new IntersectionObserver\(\n[\s\S]*?\n {4}\);\n {4}io\.observe\(root\);\n {2}\}\n/;
  const startReB = / {2}apply\(\);\n\n {2}if \(reduced\) \{\n[\s\S]*?\n {2}\} else \{\n {4}const io = new IntersectionObserver\(\n[\s\S]*?\n {4}\);\n {4}io\.observe\(root\);\n {2}\}\n/;
  const startBlock = '  ' + F.renderBlock('timeline-start', 1, 'js', F.canonicalBody('timeline-start', cls)) + '\n';
  if (startReA.test(frag)) frag = frag.replace(startReA, startBlock);
  else if (startReB.test(frag)) frag = frag.replace(startReB, startBlock);
  else skipped.push([cls, 'timeline-start', 'autoplay tail not recognized']);

  notes.timeline = true;
  return frag;
}

function migrateFile(file) {
  const source = fs.readFileSync(file, 'utf8');
  const parts = F.splitEmbed(source);
  if (!parts) { skipped.push([F.relPath(file), 'embed', 'no markers']); return; }
  const cls = F.rootClass(parts.fragment);
  if (!cls) { skipped.push([F.relPath(file), 'root-class', 'not found']); return; }
  if (F.findBlocks(parts.fragment).length) return;   // already migrated

  const notes = {};
  let frag = parts.fragment;
  frag = migrateRootRule(frag, cls, notes);
  frag = migrateControls(frag, cls, notes);
  frag = migrateCaption(frag, cls, notes);
  frag = migrateReducedMotion(frag, cls, notes);
  frag = migrateTimeline(frag, cls, notes);

  if (frag === parts.fragment) { skipped.push([F.relPath(file), 'all', 'nothing matched']); return; }
  const what = Object.keys(notes).join(',');
  console.log(`[OK] ${F.relPath(file)}: ${what || 'no blocks'}`);
  if (!dry) fs.writeFileSync(file, parts.before + frag + parts.after);
}

const files = fileArg ? [path.resolve(F.REPO_ROOT, fileArg)] : F.listDiagramFiles();
for (const f of files) migrateFile(f);
if (skipped.length) {
  console.log('\nManual attention needed:');
  for (const [f, what, why] of skipped) console.log(`  [SKIP] ${f} (${what}): ${why}`);
}
