# Distribution decision

Decision date: 2026-09-06
Status: accepted for Phase 24

## Decision

Distribute the portfolio in two layers.

### Portable core

The Python package is the public executable component. It uses only the Python standard library and produces:

- normalized `clean_data.csv`;
- `quality_report.json` with row reconciliation and rejection details;
- `report_model.json` with deterministic KPIs and aggregations.

It supports Python 3.11–3.13 and is tested through the console command `ec-sales`.

### Demonstration workbook

The verified Excel workbook and summary image demonstrate the intended client deliverable. The workbook builder remains development tooling because its current spreadsheet runtime is bundled with Codex and is not a public project dependency.

## Consequences

- The public repository remains installable without proprietary or unclear runtime dependencies.
- The core business logic is independently testable and reusable.
- The README must not claim that any arbitrary external computer can generate the Excel workbook with one command.
- A future release may add a public workbook backend after a separate license and compatibility review.

## Alternatives considered

### Bundle the current Node runtime

Rejected. The runtime is provided by the development environment and is not a declared redistributable project dependency.

### Add another spreadsheet library immediately

Deferred. Changing the workbook engine introduces new layout, chart, license, and compatibility work. It is not necessary to publish an honest portfolio demonstration of the tested Python core and verified sample workbook.

### Remove the workbook

Rejected. The workbook is the clearest evidence of the business outcome and has passed both LibreOffice and Microsoft Excel smoke tests.

## Revisit condition

Re-open this decision when a customer must run Excel generation outside the managed development environment or when packaging a standalone executable becomes a commercial requirement.
