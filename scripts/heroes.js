#!/usr/bin/env node
/*
 * heroes.js — run every hero generator in tools/heroes/, then re-expand
 * managed blocks in the regenerated diagram files.
 *
 * Usage: node scripts/heroes.js   (also: npm run heroes)
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const F = require('./lib/fragment');

const heroesDir = path.join(F.REPO_ROOT, 'tools', 'heroes');
const generators = fs.readdirSync(heroesDir)
  .filter((f) => f.endsWith('.py') && f !== 'herolib.py')
  .sort();

for (const g of generators) {
  process.stdout.write(g + ': ');
  execFileSync('python3', [path.join(heroesDir, g)], {
    cwd: F.REPO_ROOT, stdio: 'inherit',
  });
}

execFileSync(process.execPath, [path.join(__dirname, 'build.js')], {
  cwd: F.REPO_ROOT, stdio: 'inherit',
});
console.log(`[OK] ${generators.length} hero generator(s) run, blocks expanded`);
