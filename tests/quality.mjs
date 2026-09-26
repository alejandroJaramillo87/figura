#!/usr/bin/env node
// The quality gate: every check a push must pass, in one command.
//
// `npm run quality` needs Node at the version in .nvmrc and nothing else: no
// install step, because figura's checks use only Node built-ins. CI runs
// exactly this. `npm run quality:full` adds the browser tier, which needs
// `npm ci` for playwright-core and a Chromium.
//
// Every step runs even after one fails, so a single run reports everything.

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT } from "./lib/check.mjs";

const FULL = process.argv.includes("--full");

// Preflight: the gate means what CI means only on the Node version CI pins.
const pinned = readFileSync(join(ROOT, ".nvmrc"), "utf8").trim();
if (process.versions.node !== pinned) {
  console.error(`[ERROR] Node ${process.versions.node} found, .nvmrc pins ${pinned}`);
  console.error(`Solution: switch to Node ${pinned} before running the gate`);
  console.error(`Command:  nvm use`);
  process.exit(1);
}

// Preflight: a declared dependency without a lockfile is an unpinned one.
const pkg = JSON.parse(readFileSync(join(ROOT, "package.json"), "utf8"));
const declared = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies });
if (declared.length && !existsSync(join(ROOT, "package-lock.json"))) {
  console.error(`[ERROR] package.json declares ${declared.join(", ")} but there is no package-lock.json`);
  console.error(`Solution: pin exact versions and commit the lockfile`);
  console.error(`Command:  npm install --save-exact && git add package-lock.json`);
  process.exit(1);
}

const steps = [
  ["managed blocks", "node", ["scripts/build.js", "--check"]],
  ["contract", "node", ["scripts/validate.js"]],
  ["retired names", "node", ["tests/check-retired-names.mjs"]],
  ["code blocks", "node", ["tests/check-command-prompts.mjs"]],
  ["links", "node", ["tests/check-links.mjs"]],
];
if (FULL) steps.push(["render (browser)", "node", ["tests/render.test.mjs"]]);
else console.log("[SKIP] render (browser): run npm run quality:full to include it");

const failed = [];
for (const [name, cmd, args] of steps) {
  console.log(`\n== ${name}`);
  const r = spawnSync(cmd, args, { cwd: ROOT, stdio: "inherit" });
  if (r.status !== 0) failed.push(name);
}

console.log(`\n${steps.length - failed.length}/${steps.length} steps passed`);
if (failed.length) console.log(`failed: ${failed.join(", ")}`);
process.exit(failed.length ? 1 : 0);
