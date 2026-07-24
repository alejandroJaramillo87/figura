#!/usr/bin/env node
/*
 * new-diagram.js — scaffold a new diagram with managed blocks pre-expanded.
 *
 * Usage:
 *   node scripts/new-diagram.js <post-slug>/<kebab-name> \
 *     --kind step-timeline|hover-inspect|ambient \
 *     --palette classic|pastel-dark|pastel-light \
 *     --abbr <short-prefix> \
 *     [--title "Human-readable title"]
 *
 * Creates diagrams/<post-slug>/<kebab-name>.html from templates/<kind>.html,
 * expands all managed blocks, and appends a manifest.json entry. The author
 * then fills in the TODO regions: SVG, step CSS, and step handlers.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const F = require('./lib/fragment');

function arg(name, fallback) {
  const i = process.argv.indexOf('--' + name);
  return i !== -1 ? process.argv[i + 1] : fallback;
}

function fail(msg) {
  console.error('[ERROR] ' + msg);
  process.exit(2);
}

const target = process.argv[2];
if (!target || !/^[a-z0-9-]+\/[a-z0-9-]+$/.test(target)) {
  fail('first argument must be <post-slug>/<kebab-name>');
}
const [slug, name] = target.split('/');
const kind = arg('kind', 'step-timeline');
const paletteArg = arg('palette', 'classic');
const abbr = arg('abbr', null);
const title = arg('title', name.replace(/-/g, ' '));

const PALETTE_BLOCK = {
  classic: 'palette-classic',
  'pastel-dark': 'palette-pastel-dark',
  'pastel-light': 'palette-pastel-light',
};
if (!PALETTE_BLOCK[paletteArg]) fail('unknown palette: ' + paletteArg);
if (!abbr || !/^[a-z0-9]{2,6}$/.test(abbr)) fail('--abbr <2-6 char prefix> is required (e.g. kvcf)');

const tplPath = path.join(F.REPO_ROOT, 'templates', kind + '.html');
if (!fs.existsSync(tplPath)) fail('unknown kind: ' + kind);

const outPath = path.join(F.DIAGRAMS_DIR, slug, name + '.html');
if (fs.existsSync(outPath)) fail('already exists: ' + F.relPath(outPath));

const panel = paletteArg === 'pastel-light' ? 'panel-base-light' : 'panel-base';
let out = fs.readFileSync(tplPath, 'utf8')
  .replaceAll('{{NAME}}', name)
  .replaceAll('{{TITLE}}', title)
  .replaceAll('{{ABBR}}', abbr)
  .replaceAll('{{PALETTE}}', PALETTE_BLOCK[paletteArg])
  .replaceAll('{{PANEL}}', panel);

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, out);

// expand managed blocks in the new file
execFileSync(process.execPath, [path.join(__dirname, 'build.js'), '--file', F.relPath(outPath)], {
  cwd: F.REPO_ROOT, stdio: 'inherit',
});

// append manifest entry
const manifest = F.loadManifest();
manifest.push({
  id: name,
  path: F.relPath(outPath),
  title,
  post: slug,
  description: 'TODO: one-sentence description for the gallery.',
});
fs.writeFileSync(F.MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n');

console.log('[OK] created ' + F.relPath(outPath));
console.log('[OK] manifest entry appended (fill in the description)');
console.log('Next: author the SVG and step CSS, then run:');
console.log('  node scripts/build.js --check && node scripts/validate.js');
