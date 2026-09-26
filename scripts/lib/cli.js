/*
 * cli.js — argument parsing and exit handling shared by the figura scripts.
 *
 * Every script accepts only the options it declares: an unknown flag or a
 * missing option value is a usage error (exit 2). Hand-rolled parsing ignored
 * unknown flags, so a mistyped --chek ran build.js as a full rewrite.
 */
'use strict';

const { parseArgs } = require('util');

/* options: { name: { type: 'boolean' | 'string' } }; returns { values, positionals }. */
function parse(usage, options, { positionals = false } = {}) {
  try {
    return parseArgs({ options, allowPositionals: positionals, strict: true });
  } catch (e) {
    usageError(usage, e.message);
  }
}

function usageError(usage, msg) {
  console.error('[ERROR] ' + msg);
  console.error(usage.trim());
  process.exit(2);
}

function fail(msg) {
  console.error('[ERROR] ' + msg);
  process.exit(2);
}

module.exports = { parse, usageError, fail };
