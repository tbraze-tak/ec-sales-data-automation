# Phase status

Updated: 2026-09-06

## Phase 21 — Discovery / Implementation Gate

Status: complete

- Empty repository baseline recorded.
- Product scope recovered and made canonical.
- Competitive and Prior Art/IP screens completed.
- Gate decision recorded as GO with conditions.

## Phase 22 — v1 foundation and sample E2E

Status: complete for the synthetic sample

Delivered:

- versioned source-adapter contract for three fictional shops;
- explicit canonical schema and calculation policy;
- twelve synthetic input rows across three incompatible schemas;
- deterministic Python validation, normalization, duplicate handling, aggregation, and reconciliation;
- machine-readable clean data, quality report, and report model;
- seven-sheet Excel report with summary, monthly, channel, product, clean-data, quality, and provenance views;
- native charts for monthly, channel, and product results;
- dependency-free unit tests for reconciliation, exact totals, rejection behavior, and deterministic outputs;
- rendered visual review of every sheet.

Sample result:

- Input rows: 12
- Accepted rows: 10
- Exact duplicates excluded: 1
- Invalid rows rejected: 1
- Net sales: JPY 36,590
- Completed orders: 8
- Reconciliation: OK

## Phase 22 exit findings

- The workbook builder currently relies on the Codex bundled spreadsheet runtime and is not yet packaged for a clean external machine.
- Microsoft Excel desktop smoke testing remained for Phase 23.
- Malformed headers, sensitive columns, conflicting duplicates, and fatal files required dedicated tests.
- README still required a portfolio-oriented Before/After section and screenshot.

## Phase 22 next gate

Phase 23 should harden error cases, package the workbook generator for external use, validate the generated workbook in an independent office suite, and prepare public-facing documentation.

## Phase 23 — hardening and portfolio release preparation

Status: complete

- Expanded the dependency-free test suite from 2 to 8 tests.
- Added fatal-file tests for missing columns, sensitive columns, unknown sources, and empty input folders.
- Added row-level tests for invalid dates, fractional JPY values, and conflicting duplicates.
- Corrected sensitive-column detection so an ordinary field such as `product_name` is not falsely rejected.
- Added MIT project licensing and a data-safety policy.
- Added a public-facing Before/After explanation, architecture, limitations, reconciliation figures, and summary image.
- Verified the XLSX package and all rendered sheets.
- Opened and exported the workbook with LibreOffice as a seven-page PDF.
- Opened the workbook in Microsoft Excel for Mac, confirmed seven worksheets, and closed it without saving.

Remaining release limitation:

- The Python CSV/JSON pipeline is portable and uses the standard library only. The Excel builder still uses the Codex bundled spreadsheet runtime, so a publicly installable workbook backend or packaged executable is required before claiming one-command operation on an arbitrary external computer.

## Next phase

Phase 24 should choose and implement the public distribution model, then create a clean-clone installation test and a portfolio publication checklist.

## Phase 24 — public distribution

Status: complete

Completed:

- Confirmed that additional usage credits were available and resumed without consuming a reset credit.
- Chose a two-layer distribution model: portable Python core plus verified demonstration workbook.
- Added an installable `ec-sales` console command and `python -m ec_sales` entry point.
- Added portable and clean-install smoke-test scripts.
- Added GitHub Actions coverage for Python 3.11–3.13.
- Built a wheel in an isolated copy and installed it into a clean Python 3.12 virtual environment.
- Ran the installed command and verified all portable outputs and expected fixture totals.
- Updated README claims so workbook generation is not presented as portable outside the managed development environment.

## Next phase

Phase 25 should perform the pre-commit repository audit, decide whether generated demonstration artifacts belong in version control or a release attachment, and prepare the first commit. Creating a remote or publishing the repository requires explicit user direction.

## Phase 25 — pre-commit audit and bilingual delivery

Status: complete

Completed:

- Audited 36 publication candidates for secrets, personal paths, real email addresses, unsafe symlinks, and oversized files; no findings remained.
- Kept English canonical fields and implementation identifiers while adding separate Japanese and English workbook presentations.
- Generated both workbooks from the same `report_model.json` and verified identical reconciliation totals.
- Inspected all seven rendered sheets in each locale and found no layout-blocking defects.
- Verified both XLSX packages, LibreOffice opening/export, and Microsoft Excel for Mac opening with seven worksheets.
- Chose to commit only the compact summary previews; generated workbooks remain outside Git and are intended for release attachments or direct portfolio delivery.
- Confirmed that no remote is configured and no commit has been created.

## Next phase

Phase 26 may create the first local commit after an explicit user request. Remote creation and publication remain separate, explicitly authorized actions.

## Phase 26 — first local commit

Status: complete

- User explicitly requested progression to Phase 26.
- The complete first-commit candidate set will be staged and reviewed before committing.
- Automated tests, clean-install verification, and the publication audit must pass immediately before the commit.
- This phase creates a local commit only; it does not configure a remote, publish the repository, create a release, or upload workbook artifacts.
- The audited candidate set was recorded in the first local commit on `main`.
