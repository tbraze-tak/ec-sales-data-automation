# Prior Art and IP screening

Screened: 2026-09-06
Purpose: early product-risk review, not legal advice or a Freedom-to-Operate opinion.

## Prior art assessment

The broad workflow—ingest data from differing sources, map it to a normalized representation, aggregate it, and generate spreadsheet/chart reports—is longstanding and crowded.

Illustrative prior art found in a preliminary keyword search:

- [US20070078877A1 — XBRL data conversion](https://patents.google.com/patent/US20070078877A1/en) describes mapping data from CSV/SQL sources to a normalized standard and producing human-readable reports.
- [US20060112123A1 — Spreadsheet user-interfaced business data visualization and publishing system](https://patents.google.com/patent/US20060112123A1/en) describes ETL from diverse sources with spreadsheet reporting and charts.
- [US20180341956A1 — Real-Time Web Analytics System and Method](https://patents.google.com/patent/US20180341956A1/en) includes collection, cleansing, aggregation, metrics, CSV, and graphical reporting in a much broader real-time architecture.
- [US20240232202A1 — No-code platform for generating reports as a transaction](https://patents.google.com/patent/US20240232202A1/en) includes configurable data retrieval and report generation to formats such as Excel and CSV.

These records do not establish infringement or clearance. They do establish that broad novelty claims around “CSV normalization plus automatic reports” would be inappropriate. v1 should be implemented as ordinary business-process automation without copying any patent text, diagrams, claims, or proprietary product behavior.

## Copyright and provenance controls

- Write all application code and documentation from scratch in this repository.
- Generate all demo data from documented random seeds and fictional entities.
- Do not copy marketplace exports, screenshots, logos, help text, templates, or proprietary field lists.
- Use generic fictional adapters; do not label them `Amazon`, `Rakuten`, or another trademark in product-facing artifacts.
- Preserve a `NOTICE` or third-party license bundle if the tool is redistributed.
- Do not copy code from `argo-core`, employer repositories, answers, gists, or tutorials without provenance and license review.

## Open-source dependency screen

Preferred runtime dependencies:

| Dependency | Purpose | License signal | Initial decision |
|---|---|---|---|
| Python standard library | CLI, paths, CSV support, hashing | PSF license | Allow |
| pandas | parsing, normalization, aggregation | BSD-licensed per official docs | Allow with notice |
| XlsxWriter | new `.xlsx` generation, charts, formatting | BSD 2-Clause per official docs | Allow with notice |

Official sources: [pandas documentation](https://pandas.pydata.org/docs/) and [XlsxWriter license](https://xlsxwriter.readthedocs.io/license.html).

Avoid adding a dependency unless its license and necessity are recorded. Do not vendor dependency source. Lock exact versions for reproducibility, while keeping project code independent of a single current version where practical.

## Trademark and presentation controls

- Repository/project title: `EC Sales Data Automation`.
- Fictional shop names only; no third-party brand marks.
- It is acceptable to explain generically that marketplace exports often differ, but do not imply endorsement or certified integration.
- Screenshots for a public portfolio must contain only the generated workbook and synthetic values.

## Data/privacy controls

Although v1 uses synthetic data, design the schema as if customer exports may later contain personal data:

- exclude names, addresses, email, phone, payment tokens, and free-text notes from the canonical schema;
- avoid logging full raw rows;
- write outputs locally only;
- document input/output retention and safe deletion for future client work;
- fail closed on unexpected columns that appear sensitive.

## Decision

**Low initial IP risk with controls.** Proceed with a conventional, independently implemented tool. Do not market the workflow as technically novel. A professional patent/trademark review would be required before asserting exclusivity, filing claims, or launching a high-scale commercial product.
