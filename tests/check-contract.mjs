#!/usr/bin/env node
// The contract and the validator cite each other honestly.
//
// Every rule id in scripts/validate.js's RULES table is cited in
// .styles/DIAGRAM_STYLE.md after "Checked by:", beside the hard rule it
// enforces, and every id the guide cites there exists. An uncited id is a
// check nobody can find the reason for; a cited id that does not exist is a
// rule that claims enforcement it does not have.
//
// It also keeps CLAUDE.md an import list. Only the files that route to it may
// name it; everything else names AGENTS.md or the style guide that owns the
// fact, so a reader never follows a pointer into a file that holds none.

import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";
import { ROOT, trackedFiles, report } from "./lib/check.mjs";

const { RULES } = createRequire(import.meta.url)(join(ROOT, "scripts/validate.js"));
const GUIDE = ".styles/DIAGRAM_STYLE.md";
const MAY_NAME_CLAUDE = new Set(["CLAUDE.md", "AGENTS.md", "README.md", ".styles/README.md", "tests/check-contract.mjs", "tests/check-retired-names.mjs"]);

const failures = [];
const guide = readFileSync(join(ROOT, GUIDE), "utf8");
// "Checked by:" runs to the end of its sentence; its backticked words are ids
// unless they are one of the other checks it may name.
const OTHER = new Set(["tests/render.test.mjs", "export --check"]);
const cited = new Set();
for (const m of guide.matchAll(/Checked by:?([\s\S]*?)(?:\.\s|\.$)/g)) {
  for (const id of m[1].matchAll(/`([^`]+)`/g)) if (!OTHER.has(id[1])) cited.add(id[1]);
}
for (const id of Object.keys(RULES)) if (!cited.has(id)) failures.push(`${GUIDE}: validator rule ${id} is not cited after "Checked by:"`);
for (const id of cited) if (!(id in RULES)) failures.push(`${GUIDE}: cites ${id}, which scripts/validate.js does not report`);

let scanned = 0;
for (const file of trackedFiles()) {
  if (!/\.(md|mjs|js|css|html|json)$/.test(file) || MAY_NAME_CLAUDE.has(file) || file.includes("/investigations/")) continue;
  scanned++;
  readFileSync(join(ROOT, file), "utf8").split("\n").forEach((line, i) => {
    if (/(?<![\w.-])CLAUDE\.md\b/.test(line)) failures.push(`${file}:${i + 1}: names CLAUDE.md, which only imports; name AGENTS.md or the style guide instead`);
  });
}

report("contract", failures, Object.keys(RULES).length + scanned);
