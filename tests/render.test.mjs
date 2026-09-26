#!/usr/bin/env node
// Browser checks for what the validator cannot see: every diagram renders
// without a script error or a failed request, never changes height while a
// reader drives it, and jumps a step timeline to its final state under
// reduced motion. The gallery must embed every manifest entry, including the
// duplicated first one, without an error.
//
// Runs under `npm run quality:full`. It needs `npm ci` (playwright-core) and
// a Chromium: PLAYWRIGHT_CHROMIUM, or /opt/pw-browsers/chromium by default.
// The repository is served from a local static server, because the gallery's
// manifest fetch fails over file://.

import { createServer } from "node:http";
import { existsSync, readFileSync, statSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { chromium } from "playwright-core";
import { ROOT, report } from "./lib/check.mjs";

const CHROME = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const WIDTHS = [760, 360]; // the blog column, and a phone
const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".json": "application/json" };

const server = createServer((req, res) => {
  if (req.url === "/favicon.ico") return res.writeHead(204).end(); // the browser asks on its own
  const path = normalize(join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname)));
  const file = path.startsWith(ROOT) && existsSync(path) && statSync(path).isDirectory() ? join(path, "index.html") : path;
  if (!file.startsWith(ROOT) || !existsSync(file)) {
    res.writeHead(404).end();
    return;
  }
  res.writeHead(200, { "content-type": TYPES[extname(file)] || "application/octet-stream" });
  res.end(readFileSync(file));
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${server.address().port}`;

const manifest = JSON.parse(readFileSync(join(ROOT, "manifest.json"), "utf8"));
const failures = [];
let checked = 0;

// Collect what a page reports, so each visit can fail on it.
function watch(page) {
  const seen = [];
  page.on("pageerror", (e) => seen.push(`script error: ${e.message}`));
  page.on("console", (m) => m.type() === "error" && seen.push(`console error: ${m.text()}`));
  page.on("requestfailed", (r) => seen.push(`request failed: ${r.url()}`));
  page.on("response", (r) => r.status() >= 400 && seen.push(`HTTP ${r.status()}: ${r.url()}`));
  return seen;
}

// Drive every control the diagram offers and return the fragment heights seen.
// Autoplay is paused first so only the reader's actions change the state.
async function drive(page) {
  return page.evaluate(async () => {
    const root = document.querySelector(".fg-diagram");
    const heights = new Set();
    const settle = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    const measure = async () => {
      await settle();
      heights.add(Math.round(root.getBoundingClientRect().height * 2) / 2);
    };
    await measure();
    const play = root.querySelector('[data-fg="play"]');
    if (play && root.classList.contains("is-playing")) play.click();
    const next = root.querySelector('[data-fg="next"]');
    if (next) {
      const total = Number((root.querySelector('[data-fg="counter"]')?.textContent || "0 / 12").split("/")[1]);
      for (let i = 0; i <= total; i++) {
        next.click();
        await measure();
      }
    }
    for (const b of root.querySelectorAll('[data-fg="toggle"]')) {
      for (let i = 0; i < 6; i++) {
        b.click();
        await measure();
      }
    }
    for (const el of root.querySelectorAll("[data-info]")) {
      el.dispatchEvent(new MouseEvent("mouseenter"));
      el.dispatchEvent(new FocusEvent("focus"));
      await measure();
      el.dispatchEvent(new MouseEvent("mouseleave"));
      el.dispatchEvent(new FocusEvent("blur"));
    }
    await measure();
    return [...heights];
  });
}

const browser = await chromium.launch({ executablePath: CHROME });
try {
  for (const width of WIDTHS) {
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    for (const entry of manifest) {
      const page = await context.newPage();
      const seen = watch(page);
      checked++;
      await page.goto(`${BASE}/${entry.path}`, { waitUntil: "load" });
      const heights = await drive(page);
      if (heights.length > 1) {
        failures.push(`${entry.path} at ${width}px: height changes while driven (${heights.join(", ")}px)`);
      }
      for (const s of seen) failures.push(`${entry.path} at ${width}px: ${s}`);
      await page.close();
    }
    await context.close();
  }

  // Reduced motion: a step timeline shows its final state, not step 0.
  const reduced = await browser.newContext({ viewport: { width: 760, height: 900 }, reducedMotion: "reduce" });
  for (const entry of manifest.filter((e) => e.kind === "step-timeline")) {
    const page = await reduced.newPage();
    checked++;
    await page.goto(`${BASE}/${entry.path}`, { waitUntil: "load" });
    const counter = await page.textContent('.fg-diagram [data-fg="counter"]').catch(() => null);
    const [at, total] = (counter || "").split("/").map((n) => Number(n.trim()));
    if (!counter || at !== total) failures.push(`${entry.path} under reduced motion: shows step ${counter}, not the final step`);
    await page.close();
  }
  await reduced.close();

  // The gallery embeds every entry the way the blog does, the first one twice.
  const page = await browser.newPage();
  const seen = watch(page);
  checked++;
  await page.goto(`${BASE}/index.html`, { waitUntil: "networkidle" });
  await page.waitForFunction((n) => document.querySelectorAll("#gallery .entry").length === n, manifest.length);
  await page.waitForLoadState("networkidle");
  const embedded = await page.$$eval("#gallery .fg-diagram", (els) => els.length);
  const errors = await page.$$eval("#gallery .error", (els) => els.map((e) => e.textContent));
  for (const e of errors) failures.push(`gallery: ${e}`);
  if (embedded !== manifest.length + 1) failures.push(`gallery: ${embedded} diagrams embedded, expected ${manifest.length + 1}`);
  for (const s of seen) failures.push(`gallery: ${s}`);
} finally {
  await browser.close();
  server.close();
}

report("render (browser)", failures, checked);
