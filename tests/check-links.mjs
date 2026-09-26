#!/usr/bin/env node
// Internal links in repository markdown resolve.
//
// Every relative link names a file or directory that exists; anchors are not
// checked. A backticked repository path (`scripts/lib/fragment.js`) must exist
// too: a token containing a slash whose first segment is a tracked top-level
// directory, resolved from the repository root. Globs and placeholders (`*`,
// `<slug>`, `{...}`) are not paths and are skipped.
//
// A path in another repository is written with that repository's name in
// front (`curiosity-chronicles/tests/...`) or as a GitHub URL, so it cannot
// be mistaken for a path here. Links inside diagram fragments are the
// validator's (`id-ref`, `self-contained`), not this check's.

import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { ROOT, trackedFiles, report } from "./lib/check.mjs";

const failures = [];
let checked = 0;

const tracked = trackedFiles();
const topDirs = new Set(tracked.filter((f) => f.includes("/")).map((f) => f.split("/")[0]));
for (const file of tracked) {
  // Frozen records (investigations/) keep the paths they were written against.
  if (!file.endsWith(".md") || file.includes("/investigations/")) continue;
  const text = readFileSync(join(ROOT, file), "utf8").replace(/```[\s\S]*?```/g, "");
  for (const m of text.matchAll(/\]\(([^)\s]+)\)/g)) {
    const target = m[1].split("#")[0];
    if (!target || /^[a-z]+:/i.test(target)) continue;
    checked++;
    if (!existsSync(join(ROOT, dirname(file), target))) failures.push(`${file}: broken link ${m[1]}`);
  }
  for (const m of text.matchAll(/`([^`\s]+)`/g)) {
    const path = m[1].replace(/[:#].*$/, "").replace(/\/$/, "");
    if (!path.includes("/") || !topDirs.has(path.split("/")[0]) || /[*<>{}$]|\.\.\./.test(path)) continue;
    checked++;
    if (!existsSync(join(ROOT, path))) failures.push(`${file}: names a path that does not exist, ${m[1]}`);
  }
}

report("links", failures, checked);
