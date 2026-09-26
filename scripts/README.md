# Scripts

The command-line tools that scaffold, build, validate and export diagrams, all CommonJS on Node
built-ins, run through the npm scripts in `package.json`.

<!-- inventory:dirs:start -->

| Directory | Holds |
|-----------|-------|
| [lib/](lib/README.md) | Modules the scripts share: fragment parsing and block tables, argument parsing, and the report format. |

<!-- inventory:dirs:end -->

<!-- inventory:pages:start -->

| File | Holds |
|------|-------|
| [build.js](build.js) | Re-expands the managed blocks in every diagram from their canonical sources. |
| [export-svg.js](export-svg.js) | Writes each static diagram as a standalone SVG image under exports/. |
| [new-diagram.js](new-diagram.js) | Scaffolds a new diagram from its kind's template, with managed blocks expanded. |
| [validate.js](validate.js) | Contract linter for the hard rules in .styles/DIAGRAM_STYLE.md. |

<!-- inventory:pages:end -->

Each script accepts only the options it declares, and ends a check with the shared
`PASS`/`FAIL` line from `lib/report.js`.
