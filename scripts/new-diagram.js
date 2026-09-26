#!/usr/bin/env node
/*
 * new-diagram.js — scaffold a new diagram with managed blocks pre-expanded.
 *
 * Usage:
 *   node scripts/new-diagram.js <consumer-dir>/<kebab-name> \
 *     --kind step-timeline|hover-inspect|toggle|ambient|static \
 *     --abbr <2-6 char prefix> \
 *     [--title "Human-readable title"] [--palette classic]
 *
 * Creates diagrams/<consumer-dir>/<kebab-name>.html from templates/<kind>.html
 * with every managed block expanded, and appends a manifest.json entry. The
 * author then fills in the TODO regions, which the validator refuses until
 * they are gone. Nothing is written unless every input is valid and the
 * blocks expand; the manifest is replaced atomically, and the new file is
 * removed again if that fails.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const F = require('./lib/fragment');
const cli = require('./lib/cli');
const { expandSource } = require('./build');

const USAGE = `usage: node scripts/new-diagram.js <consumer-dir>/<kebab-name> --kind <${Object.keys(F.KIND_BLOCKS).join('|')}> --abbr <2-6 chars> [--title "..."] [--palette classic]`;
const PALETTE_BLOCK = { classic: 'palette-classic' };

const { values, positionals } = cli.parse(USAGE, {
  kind: { type: 'string' },
  abbr: { type: 'string' },
  title: { type: 'string' },
  palette: { type: 'string', default: 'classic' },
}, { positionals: true });

const target = positionals[0];
if (positionals.length !== 1 || !/^[a-z0-9]+(?:-[a-z0-9]+)*\/[a-z0-9]+(?:-[a-z0-9]+)*$/.test(target)) {
  cli.usageError(USAGE, 'first argument must be <consumer-dir>/<kebab-name>, lowercase kebab-case');
}
const [slug, name] = target.split('/');
const { kind, abbr } = values;
const title = values.title || name.replace(/-/g, ' ');

if (!kind || !(kind in F.KIND_BLOCKS)) cli.usageError(USAGE, '--kind must be one of ' + Object.keys(F.KIND_BLOCKS).join(', '));
if (!PALETTE_BLOCK[values.palette]) cli.fail('unknown palette: ' + values.palette);
if (!abbr || !/^[a-z0-9]{2,6}$/.test(abbr)) cli.usageError(USAGE, '--abbr <2-6 lowercase chars> is required (e.g. kvcf)');
if (/[<>"&]/.test(title)) cli.fail('--title may not contain <, >, " or &');

const outPath = path.join(F.DIAGRAMS_DIR, slug, name + '.html');
if (fs.existsSync(outPath)) cli.fail('already exists: ' + F.relPath(outPath));

const manifest = F.loadManifest();
if (manifest.some((e) => e.id === name)) cli.fail(`manifest id "${name}" is already taken`);

// the abbreviation prefixes ids and keyframes, which are page-global
for (const file of F.listDiagramFiles()) {
  const src = fs.readFileSync(file, 'utf8');
  if (new RegExp(`\\bid="${abbr}-|@keyframes fg-${abbr}-|class="${abbr}-`).test(src)) {
    cli.fail(`abbreviation "${abbr}" is already used by ${F.relPath(file)}`);
  }
}

const tpl = fs.readFileSync(path.join(F.REPO_ROOT, 'templates', kind + '.html'), 'utf8')
  .replaceAll('{{NAME}}', name)
  .replaceAll('{{TITLE}}', title)
  .replaceAll('{{ABBR}}', abbr)
  .replaceAll('{{PALETTE}}', PALETTE_BLOCK[values.palette])
  .replaceAll('{{PANEL}}', 'panel-base');
const r = expandSource(tpl);
if (r.error || r.unknown.length) cli.fail('template did not expand: ' + (r.error || 'unknown blocks ' + r.unknown.join(', ')));

manifest.push({
  id: name,
  path: F.relPath(outPath),
  title,
  post: slug,
  kind,
  description: 'TODO: one-sentence description for the gallery.',
});

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, r.rebuilt, { flag: 'wx' });
try {
  const tmp = F.MANIFEST_PATH + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(manifest, null, 2) + '\n');
  fs.renameSync(tmp, F.MANIFEST_PATH);
} catch (e) {
  fs.unlinkSync(outPath);
  cli.fail('manifest.json not updated, scaffold removed: ' + e.message);
}

console.log('[OK] created ' + F.relPath(outPath));
console.log('[OK] manifest entry appended (fill in the description)');
console.log('Next: author the SVG and styles, then run: npm run check');
