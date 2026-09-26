// Shared plumbing for the tests/check-*.mjs gates: the repository root, the
// tracked-file list, and the report format scripts/lib/report.js also uses,
// so every step of `npm run quality` reads the same.

import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");

// Tracked files only, so exports or scratch output left in the tree never
// reach a check.
export function trackedFiles() {
  return execFileSync("git", ["ls-files", "-z"], { cwd: ROOT, encoding: "utf8" })
    .split("\0")
    .filter(Boolean);
}

// Print one line per failure, then a summary; exit nonzero on any failure.
// A check that examined nothing fails too: an input pattern that stopped
// matching would otherwise report PASS forever.
export function report(name, failures, checked) {
  if (checked === 0 && !failures.length) failures = [`${name}: checked nothing; its inputs were not found`];
  for (const f of failures) console.error(`  FAIL  ${f}`);
  const status = failures.length ? "FAIL" : "PASS";
  console.log(`${status}  ${name}: ${checked} checked, ${failures.length} failed`);
  process.exit(failures.length ? 1 : 0);
}
