/*
 * The one summary format every figura check ends with, for the CommonJS
 * scripts. tests/lib/check.mjs holds the same function for the ESM checks;
 * keep the two texts identical so `npm run quality` output reads the same
 * whichever side a step runs on.
 *
 * A check that examined nothing fails: an input pattern that stopped
 * matching would otherwise report PASS forever.
 */
'use strict';

function report(name, failures, checked) {
  if (checked === 0 && !failures.length) failures = [`${name}: checked nothing; its inputs were not found`];
  for (const f of failures) console.error(`  FAIL  ${f}`);
  const status = failures.length ? 'FAIL' : 'PASS';
  console.log(`${status}  ${name}: ${checked} checked, ${failures.length} failed`);
  process.exit(failures.length ? 1 : 0);
}

module.exports = { report };
