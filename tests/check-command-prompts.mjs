#!/usr/bin/env node
// Code blocks in repository markdown name their language, and shell blocks carry no prompt marker.
//
// A command block is pasted, not read: pasted into a shell, a leading `$ `
// fails as "command not found" and the block silently runs nothing. A block
// that must show a command beside its output is a transcript and is tagged
// `console` instead, which the prompt rule does not read. An untagged fence
// renders without highlighting and leaves the reader to guess what it holds.
// Frozen records (investigations/) are exempt: they are history.

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT, trackedFiles, report } from "./lib/check.mjs";

const SHELL = new Set(["bash", "sh", "shell", "zsh"]);
const failures = [];
let checked = 0;

for (const file of trackedFiles()) {
  if (!file.endsWith(".md") || file.includes("/investigations/")) continue;
  let open = null; // the fence and language of the block being read, or null
  readFileSync(join(ROOT, file), "utf8")
    .split("\n")
    .forEach((line, i) => {
      const fence = line.match(/^\s*(`{3,}|~{3,})\s*([^`\s]*)/);
      if (open) {
        if (fence && fence[1][0] === open.fence[0] && fence[1].length >= open.fence.length && !fence[2]) open = null;
        else if (SHELL.has(open.lang) && /^\s*\$ /.test(line)) failures.push(`${file}:${i + 1}: prompt marker in a ${open.lang} block`);
        return;
      }
      if (!fence) return;
      checked++;
      open = { fence: fence[1], lang: fence[2] };
      if (!open.lang) failures.push(`${file}:${i + 1}: code block has no language tag`);
    });
}

report("code blocks", failures, checked);
