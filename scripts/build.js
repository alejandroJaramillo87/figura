#!/usr/bin/env node
/*
 * Re-expands the managed blocks in every diagram from their canonical sources.
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
const cli = require('./lib/cli');
const { report } = require('./lib/report');

const USAGE = 'usage: node scripts/build.js [--check] [--file diagrams/<slug>/<name>.html]';

function expandFile(file) {
  return { file, ...expandSource(fs.readFileSync(file, 'utf8')) };
}

/* Re-expand every managed block in one diagram's source text. */
function expandSource(source) {
  const parts = F.splitEmbed(source);
  if (!parts) return { error: 'missing embed markers' };
  const cls = F.rootClass(parts.fragment);
  if (!cls) return { error: 'missing root class (fg-diagram fg-<name>)' };

  let blocks;
  try {
    blocks = F.findBlocks(parts.fragment);
  } catch (e) {
    return { error: e.message };
  }
  const unknown = [];
  let out = '';
  let cursor = 0;
  for (const b of blocks) {
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
  return { source, rebuilt, changed: rebuilt !== source, unknown };
}

function main() {
  const { values } = cli.parse(USAGE, { check: { type: 'boolean' }, file: { type: 'string' } });
  const check = !!values.check;
  const fileArg = values.file || null;
  if (fileArg && !fs.existsSync(path.resolve(F.REPO_ROOT, fileArg))) cli.fail('no such file: ' + fileArg);

  const files = fileArg ? [path.resolve(F.REPO_ROOT, fileArg)] : F.listDiagramFiles();
  const failures = [];
  let written = 0;

  for (const file of files) {
    const r = expandFile(file);
    if (r.error) {
      failures.push(`${F.relPath(file)}: ${r.error}`);
      continue;
    }
    for (const name of r.unknown) {
      failures.push(`${F.relPath(file)}: unknown managed block "${name}"`);
    }
    if (!r.changed) continue;
    if (check) {
      failures.push(`${F.relPath(file)}: managed blocks differ from their canonical source (run npm run build)`);
    } else {
      fs.writeFileSync(file, r.rebuilt);
      console.log(`[OK] ${F.relPath(file)}: managed blocks re-expanded`);
      written++;
    }
  }

  if (!check) console.log(`build: ${written} of ${files.length} files updated`);
  report(check ? 'build --check' : 'build', failures, files.length);
}

if (require.main === module) main();

module.exports = { expandSource };
