#!/usr/bin/env node
/*
 * build.js — re-expand managed blocks in every diagram from canonical sources.
 *
 * Managed blocks (see scripts/lib/fragment.js for the sentinel syntax) are
 * owned by this script: their contents are replaced from shared/runtime/
 * templates and the palettes derived from shared/tokens.css. Running twice
 * produces no further changes (idempotent).
 *
 * Usage:
 *   node scripts/build.js            # rewrite all diagrams in place
 *   node scripts/build.js --check    # no writes; exit 1 if any block drifted
 *   node scripts/build.js --file diagrams/<slug>/<name>.html
 */
'use strict';

const fs = require('fs');
const path = require('path');
const F = require('./lib/fragment');

function expandFile(file) {
  const source = fs.readFileSync(file, 'utf8');
  const parts = F.splitEmbed(source);
  if (!parts) return { file, error: 'missing embed markers' };
  const cls = F.rootClass(parts.fragment);
  if (!cls) return { file, error: 'missing root class (fg-diagram fg-<name>)' };

  const unknown = [];
  let out = '';
  let cursor = 0;
  for (const b of F.findBlocks(parts.fragment)) {
    const body = F.canonicalBody(b.name, cls);
    if (body === null) {
      unknown.push(b.name);
      continue;
    }
    out += parts.fragment.slice(cursor, b.start);
    // re-indent to match the begin marker's indentation
    const indentMatch = parts.fragment.slice(0, b.start).match(/(?:^|\n)([ \t]*)$/);
    const indent = indentMatch ? indentMatch[1] : '';
    const rendered = F.renderBlock(b.name, b.version, b.style, body)
      .split('\n')
      .map((l, i) => (i === 0 || !l ? l : indent + l))
      .join('\n');
    out += rendered;
    cursor = b.end;
  }
  out += parts.fragment.slice(cursor);

  const rebuilt = parts.before + out + parts.after;
  return { file, source, rebuilt, changed: rebuilt !== source, unknown };
}

function main() {
  const args = process.argv.slice(2);
  const check = args.includes('--check');
  const fileArg = args.includes('--file') ? args[args.indexOf('--file') + 1] : null;

  const files = fileArg ? [path.resolve(F.REPO_ROOT, fileArg)] : F.listDiagramFiles();
  let drifted = 0, errors = 0, written = 0;

  for (const file of files) {
    const r = expandFile(file);
    if (r.error) {
      console.error(`[ERROR] ${F.relPath(file)}: ${r.error}`);
      errors++;
      continue;
    }
    for (const name of r.unknown) {
      console.error(`[ERROR] ${F.relPath(file)}: unknown managed block "${name}"`);
      errors++;
    }
    if (!r.changed) continue;
    if (check) {
      console.error(`[DRIFT] ${F.relPath(file)}: managed blocks differ from canonical source`);
      drifted++;
    } else {
      fs.writeFileSync(file, r.rebuilt);
      console.log(`[OK] ${F.relPath(file)}: managed blocks re-expanded`);
      written++;
    }
  }

  const total = files.length;
  if (check) {
    console.error(`build --check: ${total} files, ${drifted} drifted, ${errors} errors`);
    process.exit(drifted || errors ? 1 : 0);
  }
  console.log(`build: ${total} files, ${written} updated, ${errors} errors`);
  process.exit(errors ? 1 : 0);
}

main();
