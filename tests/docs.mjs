#!/usr/bin/env node
// Generate, or with --check verify, the derived parts of the repository's
// markdown: the router tables in every README, the roster tables over the
// style guides, agents and commands, and the tables of contents in long
// documents. All are committed so a reader needs to run nothing, and all are
// rendered from the tree so none can drift from it.
//
// Router tables. Every tracked directory carries a README.md (hidden
// directories and those in NOT_ROUTED excepted) with one or both tables
// between markers:
//
//   <!-- inventory:dirs:start -->   ... <!-- inventory:dirs:end -->
//   <!-- inventory:pages:start -->  ... <!-- inventory:pages:end -->
//
// Each row links an entry and states what it holds, in the first sentence of
// the entry's own description: a directory's README intro, a document's intro,
// or a code file's header comment. An entry with none (a runtime block, a
// template, a data file) is described in the parent README with
// `<!-- describe NAME: text -->`. The root README routes directories only.
//
// Rosters. A document with `<!-- inventory:NAME:start -->` markers gets a
// table rendered from the file that owns the fact:
//   guides    .styles/*.md intros
//   agents    .claude/agents/*.md front matter
//   commands  .claude/commands/*.md front matter
//   blocks    BLOCK_VERSIONS in scripts/lib/fragment.js, described by the
//             describe lines in shared/runtime/README.md
//   tokens    shared/tokens.css, each token's trailing comment
//   rules     RULES in scripts/validate.js
//   catalog   manifest.json, grouped by consumer directory
//
// Tables of contents. A document over 500 words with four or
// more H2/H3 headings carries `## Table of Contents` and a list between
// `<!-- toc:start -->` and `<!-- toc:end -->`, rendered from its headings.
// READMEs and frozen records (under an investigations/ directory) are exempt.
//
// Usage: node tests/docs.mjs          rewrite every table in place
//        node tests/docs.mjs --check  fail on any table that would change

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { basename, join } from "node:path";
import { ROOT, trackedFiles, report } from "./lib/check.mjs";

const require = createRequire(import.meta.url);
const { BLOCK_VERSIONS } = require(join(ROOT, "scripts/lib/fragment.js"));
const { RULES } = require(join(ROOT, "scripts/validate.js"));

const CHECK = process.argv.includes("--check");

// Routed from their parent, never descended into: generated output, and the
// per-consumer diagram directories, which the manifest catalog in
// diagrams/README.md covers instead of a README each.
const NOT_ROUTED = ["exports", "node_modules"];
const notRoutedDir = (p) => /^diagrams\/[^/]+$/.test(p);

const files = trackedFiles();
const failures = [];
let changed = 0;

const read = (p) => readFileSync(join(ROOT, p), "utf8");
const isHidden = (p) => p.split("/").some((s) => s.startsWith("."));
const notRouted = (p) => NOT_ROUTED.some((n) => p === n || p.startsWith(`${n}/`)) || /^diagrams\/[^/]+(\/|$)/.test(p);

// First sentence of a run of prose, markdown and comment markers flattened.
function firstSentence(text) {
  // Links are reduced to their text: a relative link is only valid from the
  // file it was written in, not from the parent README that quotes it.
  const flat = text.replace(/\[([^\]]*)\]\([^)]*\)/g, "$1").replace(/\s+/g, " ").trim();
  const m = flat.match(/^(.+?\.)(\s|$)/);
  return m ? m[1] : flat;
}

// The intro paragraph of a markdown document: the first paragraph after the H1
// that is not a bold document-class line.
function mdIntro(text) {
  const body = text.replace(/^---\n[\s\S]*?\n---\n/, "").replace(/```[\s\S]*?```/g, "").split(/^# .*$/m)[1] ?? "";
  const para = body
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .find((p) => p && !p.startsWith("**") && !p.startsWith("<!--") && !p.startsWith("#") && !p.startsWith("|"));
  return para ? firstSentence(para) : null;
}

// The leading comment of a code file, in any comment syntax the tree uses.
function headerComment(text) {
  const src = text.replace(/^#!.*\n/, "").trimStart();
  const patterns = [
    /^\/\*([\s\S]*?)\*\//, // CSS / JS block
    /^((?:\/\/.*\n?)+)/, // JS line comments
    /^((?:#.*\n?)+)/, // YAML
  ];
  for (const re of patterns) {
    const m = src.match(re);
    if (m) {
      const body = m[1].replace(/^\s*(\/\/|#|\*)+ ?/gm, "").trim();
      if (body) return firstSentence(body.split(/\n\s*\n/)[0]);
    }
  }
  return null;
}

// Immediate children of dir: { dirs, pages }, README.md excluded.
function children(dir) {
  const prefix = dir ? `${dir}/` : "";
  const dirs = new Set();
  const pages = new Set();
  for (const f of files) {
    if (!f.startsWith(prefix)) continue;
    const [head, ...rest] = f.slice(prefix.length).split("/");
    const path = prefix + head;
    if (rest.length || NOT_ROUTED.includes(path) || notRoutedDir(path)) dirs.add(head);
    else if (head !== "README.md") pages.add(head);
  }
  return { dirs: [...dirs].sort(), pages: [...pages].sort() };
}

function describe(dir, name, isDir, overrides) {
  if (overrides.has(name)) return overrides.get(name);
  const path = dir ? `${dir}/${name}` : name;
  if (isDir) return existsSync(join(ROOT, path, "README.md")) ? mdIntro(read(`${path}/README.md`)) : null;
  const text = read(path);
  if (name.endsWith(".md")) return mdIntro(text);
  return headerComment(text);
}

function table(dir, names, isDir, overrides) {
  const head = isDir ? "| Directory | Holds |\n|-----------|-------|" : "| File | Holds |\n|------|-------|";
  const rows = names.map((name) => {
    const path = dir ? `${dir}/${name}` : name;
    const desc = describe(dir, name, isDir, overrides);
    if (!desc) failures.push(`${dir || "."}/README.md: no description for ${name} (add a header comment, an intro, or <!-- describe ${name}: ... -->)`);
    else if (desc.endsWith(":")) failures.push(`${dir || "."}/README.md: the description of ${name} ends in a colon; its first sentence must stand alone`);
    const link = isDir && existsSync(join(ROOT, path, "README.md")) ? `${name}/README.md` : isDir ? `${name}/` : name;
    return `| [${isDir ? `${name}/` : name}](${link}) | ${(desc ?? "UNDESCRIBED").replace(/\|/g, "\\|")} |`;
  });
  return `${head}\n${rows.join("\n")}`;
}

function replaceBlock(text, marker, content) {
  const re = new RegExp(`(<!-- ${marker}:start -->)[\\s\\S]*?(<!-- ${marker}:end -->)`);
  return re.test(text) ? text.replace(re, (_, a, b) => `${a}\n\n${content}\n\n${b}`) : null;
}

function write(path, before, after) {
  if (before === after) return;
  changed++;
  if (CHECK) failures.push(`${path}: out of date (run: npm run docs)`);
  else writeFileSync(join(ROOT, path), after);
}

// Router READMEs.
const allDirs = new Set([""]);
for (const f of files) {
  const parts = f.split("/");
  for (let i = 1; i < parts.length; i++) allDirs.add(parts.slice(0, i).join("/"));
}
const routers = [...allDirs].filter((d) => d === "" || (!isHidden(d) && !notRouted(d))).sort();

for (const dir of routers) {
  const readme = dir ? `${dir}/README.md` : "README.md";
  if (!existsSync(join(ROOT, readme))) {
    failures.push(`${readme}: missing`);
    continue;
  }
  const before = read(readme);
  const overrides = new Map([...before.matchAll(/<!-- describe (\S+?): ([\s\S]*?) -->/g)].map((m) => [m[1], m[2].replace(/\s+/g, " ")]));
  let { dirs, pages } = children(dir);
  if (dir === "") pages = [];
  // The per-consumer directories are catalogued from the manifest instead.
  if (dir === "diagrams") dirs = [];
  let after = before;
  for (const [marker, names, isDir] of [["inventory:dirs", dirs, true], ["inventory:pages", pages, false]]) {
    if (!names.length) continue;
    const next = replaceBlock(after, marker, table(dir, names, isDir, overrides));
    if (next === null) failures.push(`${readme}: needs <!-- ${marker}:start --> / <!-- ${marker}:end -->`);
    else after = next;
  }
  write(readme, before, after);
}

// Rosters.
const fmField = (text, k) => text.match(/^---\n([\s\S]*?)\n---/)?.[1].match(new RegExp(`^${k}:\\s*(.*)$`, "m"))?.[1].trim();
const ROSTERS = {
  "inventory:guides": () => {
    const rows = files
      .filter((f) => /^\.styles\/[^/]+\.md$/.test(f) && basename(f) !== "README.md")
      .map((f) => `| [${basename(f)}](${basename(f)}) | ${mdIntro(read(f)) ?? "UNDESCRIBED"} |`);
    return `| Guide | Governs |\n|-------|---------|\n${rows.join("\n")}`;
  },
  "inventory:agents": () => {
    const rows = files
      .filter((f) => /^\.claude\/agents\/[^/]+\.md$/.test(f))
      .map((f) => `| \`${basename(f, ".md")}\` | ${fmField(read(f), "tools")} | ${fmField(read(f), "description")} |`);
    return `| Agent | Tools | Role |\n|-------|-------|------|\n${rows.join("\n")}`;
  },
  "inventory:commands": () => {
    const rows = files
      .filter((f) => /^\.claude\/commands\/[^/]+\.md$/.test(f))
      .map((f) => {
        const hint = fmField(read(f), "argument-hint");
        return `| \`/${basename(f, ".md")}${hint ? ` ${hint}` : ""}\` | ${fmField(read(f), "description")} |`;
      });
    return `| Command | Does |\n|---------|------|\n${rows.join("\n")}`;
  },
};
const cell = (s) => s.replace(/\|/g, "\\|");
ROSTERS["inventory:blocks"] = () => {
  const text = read("shared/runtime/README.md");
  const said = new Map([...text.matchAll(/<!-- describe (\S+?): ([\s\S]*?) -->/g)].map((m) => [m[1].replace(/\.(css|js)$/, ""), m[2].replace(/\s+/g, " ")]));
  const rows = Object.keys(BLOCK_VERSIONS).map((b) => `| \`${b}\` | ${cell(said.get(b) ?? "UNDESCRIBED")} |`);
  return `| Block | Provides |\n|-------|----------|\n${rows.join("\n")}`;
};
ROSTERS["inventory:tokens"] = () => {
  const rows = [...read("shared/tokens.css").matchAll(/^\s*--fg-([\w-]+):\s*([^;]+);[ \t]*(?:\/\*\s*(.*?)\s*\*\/)?/gm)]
    .map((m) => `| \`--${m[1]}\` | \`${cell(m[2].trim())}\` | ${cell(m[3] ?? "UNDESCRIBED")} |`);
  return `| Token | Value | Use |\n|-------|-------|-----|\n${rows.join("\n")}`;
};
ROSTERS["inventory:rules"] = () => {
  const rows = Object.entries(RULES).map(([id, what]) => `| \`${id}\` | ${cell(what)} |`);
  return `| Rule | Fails unless |\n|------|--------------|\n${rows.join("\n")}`;
};
ROSTERS["inventory:catalog"] = () => {
  const manifest = JSON.parse(read("manifest.json"));
  const groups = new Map();
  for (const e of manifest) {
    const dir = e.path.split("/")[1];
    if (!groups.has(dir)) groups.set(dir, []);
    groups.get(dir).push(e);
  }
  return [...groups.keys()].sort().map((dir) => {
    const rows = groups.get(dir).sort((a, b) => a.id.localeCompare(b.id)).map((e) => {
      const used = e.consumers.length ? e.consumers.map((c) => `\`${c}\``).join("<br>") : "none";
      return `| [${e.id}](${dir}/${e.id}.html) | ${e.kind} | ${cell(firstSentence(e.description))} | ${used} |`;
    });
    return `### ${dir}\n\n| Diagram | Kind | Shows | Used by |\n|---------|------|-------|---------|\n${rows.join("\n")}`;
  }).join("\n\n");
};
const rostered = files.filter((f) => f.endsWith(".md") && Object.keys(ROSTERS).some((k) => read(f).includes(`<!-- ${k}:start -->`)));
for (const doc of rostered) {
  const before = read(doc);
  let after = before;
  for (const [marker, render] of Object.entries(ROSTERS)) {
    if (after.includes(`<!-- ${marker}:start -->`)) after = replaceBlock(after, marker, render().replace(/UNDESCRIBED/g, (u) => (failures.push(`${doc}: a ${marker} row has no description`), u)));
  }
  write(doc, before, after);
}

// Tables of contents.
const slug = (h) =>
  h.toLowerCase().replace(/`/g, "").replace(/[^\p{L}\p{N}\s_-]/gu, "").trim().replace(/\s/g, "-");

const docs = files.filter(
  (f) => f.endsWith(".md") && basename(f) !== "README.md" && !f.includes("/investigations/") && !notRouted(f) && !f.startsWith(".claude/"),
);
for (const doc of docs) {
  const before = read(doc);
  const prose = before.replace(/```[\s\S]*?```/g, "");
  const heads = [...prose.matchAll(/^(##|###) (.+)$/gm)].filter((m) => m[2] !== "Table of Contents");
  const words = prose.split(/\s+/).filter(Boolean).length;
  const hasMarkers = before.includes("<!-- toc:start -->");
  if (!hasMarkers && (words <= 500 || heads.length < 4)) continue;

  let n = 0;
  const list = heads
    .map((m) => (m[1] === "##" ? `${++n}. [${m[2]}](#${slug(m[2])})` : `   - [${m[2]}](#${slug(m[2])})`))
    .join("\n");
  let after = replaceBlock(before, "toc", list);
  if (after === null) {
    // Insert the section after the intro paragraph that follows the H1.
    after = before.replace(/(^# .*\n\n(?:\*\*.*\n(?:.+\n)*\n)?(?:.+\n)+)/m, `$1\n## Table of Contents\n\n<!-- toc:start -->\n\n${list}\n\n<!-- toc:end -->\n`);
    if (after === before) {
      failures.push(`${doc}: needs a table of contents, and has no H1 and intro paragraph to insert one after`);
      continue;
    }
  }
  write(doc, before, after);
}

if (CHECK) report("docs (router tables, rosters, tables of contents)", failures, routers.length + rostered.length + docs.length);
else {
  for (const f of failures) console.error(`  FAIL  ${f}`);
  console.log(`docs: ${changed} file(s) rewritten, ${failures.length} problem(s)`);
  process.exit(failures.length ? 1 : 0);
}
