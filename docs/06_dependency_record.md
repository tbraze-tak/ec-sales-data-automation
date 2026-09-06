# Dependency record

Updated: 2026-09-06

## Runtime

- Python 3.11 or newer
- Python pipeline runtime dependencies: standard library only
- Workbook authoring during this phase: `@oai/artifact-tool` 2.8.58+ from the Codex bundled spreadsheet runtime
- Public package build backend: setuptools

## Development policy

- No code or package is vendored into this repository.
- `node_modules` is a local ignored symlink to the Codex-provided runtime.
- The Python normalization, validation, reconciliation, and aggregation layers are independent of the workbook authoring runtime.
- The public Python core does not depend on the workbook-authoring runtime. The workbook is distributed as a verified demonstration artifact; its builder remains development tooling.

## License screen

The initial screening of potential public dependencies is recorded in `docs/03_prior_art_and_ip.md`. Any added production dependency requires a recorded purpose, license, exact version, and source URL.
