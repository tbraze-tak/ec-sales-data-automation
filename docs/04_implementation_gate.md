# Implementation Gate

Decision date: 2026-09-06
Decision: **GO with conditions**

## Gate results

| Gate | Result | Basis / condition |
|---|---|---|
| Repository isolation | PASS | Dedicated empty repository confirmed; `AGENTS.md` prohibits reuse or changes to work repositories. |
| Canonical scope | PASS | v1 inputs, normalized data, outputs, exclusions, and success criteria are fixed in `01_product_brief.md`. |
| User value | PASS | Demonstrates a common paid task: reconciling heterogeneous CSV exports and producing a reusable report. |
| Competitive rationale | PASS | Mature alternatives exist; v1 differentiates through cross-schema adapters, lineage, reconciliation, local execution, and delivery quality. |
| Prior Art / IP | PASS WITH CONTROLS | Broad workflow is established; independent implementation, fictional branding, synthetic data, and modest claims are mandatory. |
| Privacy/confidentiality | PASS WITH CONTROLS | Synthetic data only in development; canonical schema excludes direct personal data; unexpected sensitive fields must fail closed. |
| Technical feasibility | PASS | Python, pandas, and XlsxWriter cover the planned pipeline and workbook generation on macOS. |
| Testability | PASS | Deterministic fixtures and exact reconciliation provide objective acceptance checks. |
| Excel verification | CONDITIONAL | Structural and LibreOffice verification can run now. Final Microsoft Excel smoke test is deferred until Excel is available. |
| Requirements ambiguity | CONDITIONAL | Refunds, cancellations, taxes, shipping, duplicates, and month-over-month baseline must be specified in a versioned data contract before pipeline coding. |

## Mandatory pre-code conditions

The implementation phase may begin only after these artifacts are added:

1. A versioned canonical schema and metric definitions.
2. Three source-adapter contracts with required/optional columns and parsing rules.
3. A deterministic synthetic-data specification covering clean and malformed cases.
4. Acceptance fixtures with known totals.
5. A dependency/license record and locked environment.

## Proposed v1 calculation policy

These defaults should become the data contract unless deliberately revised:

- `gross_sales = quantity × unit_price`
- `net_sales = gross_sales - discount_amount + shipping_amount + tax_amount`
- cancelled orders contribute zero and remain visible in quality/audit counts;
- refunds are explicit negative transactions referencing the original order where available;
- duplicate identity is source channel + order ID + product ID + transaction type, with duplicate conflicts rejected rather than silently dropped;
- all v1 rows use JPY and no currency conversion occurs;
- timestamps normalize to Asia/Tokyo and reports group by local calendar month;
- month-over-month is blank when there is no preceding month, never forced to zero.

## Implementation slices after the gate

1. Contracts and synthetic fixture generator.
2. Adapter parsing and validation.
3. Canonical merge, reconciliation, and metric engine.
4. Workbook generation.
5. CLI and one-command workflow.
6. Automated tests, workbook inspection, README, and portfolio screenshots.

## Stop conditions

Pause and re-open the gate if implementation would require:

- real marketplace/customer data;
- code, data, or know-how from `argo-core` or an employer repository;
- undocumented schema guessing;
- external credentials or account access;
- accounting/tax assertions;
- a dependency with unclear or incompatible licensing.

## Final gate statement

The project is suitable to implement as a portfolio-grade local automation tool. Coding should start with contracts and fixtures, not the reporting UI. The gate does not authorize use of real business data and does not claim patent clearance.
