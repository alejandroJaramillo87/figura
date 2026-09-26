#!/usr/bin/env node
// Retired paths stay retired. When a file is renamed or removed, its old path
// goes in RETIRED with its replacement; any tracked text that still names the
// old path fails the gate, so a rename cannot leave stragglers behind.
//
// An old name matches only as a whole token, so templates/hero.html does not
// match a longer path that ends the same way, and `npm run check` does not
// match `npm run check:x`. The same scan fails any `npm run X` whose script is
// not in package.json, which is how a renamed script is caught before it is
// retired.
//
// Exempt: this file (it must name the old paths) and frozen records under any
// investigations/ directory, whose paths are history.

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT, trackedFiles, report } from "./lib/check.mjs";

const RETIRED = [
  ["scripts/heroes.js", "nothing (the hero kind was removed)"],
  ["scripts/migrate.js", "scripts/build.js (the one-off migration is done)"],
  ["templates/hero.html", "nothing (the hero kind was removed)"],
  ["templates/hero.py", "nothing (the hero kind was removed)"],
  ["shared/runtime/hero-start.js", "shared/runtime/timeline-start.js"],
  ["shared/runtime/panel-base-light.css", "shared/runtime/panel-base.css (one palette)"],
  ["tools/heroes", "nothing (the hero kind was removed)"],
];

const EXEMPT = ["tests/check-retired-names.mjs"];
const TEXT = /\.(md|mjs|js|json|css|html|ya?ml)$/;

// Guarded on both sides: no path or word character may continue the name.
const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const pattern = (old) => new RegExp(`(?<![\\w./-])${escape(old)}(?![\\w:/-])`);
const PATTERNS = RETIRED.map(([old, now]) => [old, now, pattern(old)]);
const SCRIPTS = new Set(Object.keys(JSON.parse(readFileSync(join(ROOT, "package.json"), "utf8")).scripts));

const failures = [];
// A replacement that matches its own retired pattern would fail every file
// that follows the advice.
for (const [old, now, re] of PATTERNS) if (re.test(now)) failures.push(`RETIRED: the replacement for ${old} matches its own pattern`);

const scanned = trackedFiles().filter(
  (f) => TEXT.test(f) && !f.includes("/investigations/") && !EXEMPT.includes(f),
);
for (const file of scanned) {
  const lines = readFileSync(join(ROOT, file), "utf8").split("\n");
  lines.forEach((line, i) => {
    for (const [old, now, re] of PATTERNS) {
      if (re.test(line)) failures.push(`${file}:${i + 1}: names ${old} (now ${now})`);
    }
    for (const m of line.matchAll(/npm run ([\w:-]*[\w-])/g)) {
      if (!SCRIPTS.has(m[1]) && !PATTERNS.some(([old]) => old === `npm run ${m[1]}`)) {
        failures.push(`${file}:${i + 1}: npm run ${m[1]} is not a script in package.json`);
      }
    }
  });
}

report("retired names", failures, scanned.length);
