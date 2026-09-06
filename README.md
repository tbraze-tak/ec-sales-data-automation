# EC Sales Data Automation

[日本語](README.ja.md) | English

A portfolio project that locally validates, normalizes, and aggregates sales CSVs with different column names, date formats, and amount representations, then prepares an auditable management report.

> Different CSV layouts in, validated management workbook out.

![English sample summary](docs/assets/sample_summary_en.png)

## Project status

- Current phase: Phase 27 complete — local release package and publication-readiness verification
- Gate decision: **GO with conditions**
- Implementation: synthetic sample E2E complete
- Canonical scope: [`docs/01_product_brief.md`](docs/01_product_brief.md)
- Gate record: [`docs/04_implementation_gate.md`](docs/04_implementation_gate.md)

## Hard boundaries

- Use only wholly synthetic input data created from scratch.
- Do not use internal company data, customer data, private documents, source code, or logs.
- Keep this project isolated from `argo-core` and all employer-related repositories.
- Use fictional store and product names, with no third-party marketplace branding or affiliation claims.

## Target user experience

```text
Place CSV files in input/
        ↓
Run one command
        ↓
Produce validation results + normalized data + report outputs
```

## Before / After

Before:

- Each shop exports a different schema, date format, and status vocabulary.
- Duplicate rows, cancellations, refunds, and malformed values require manual decisions.
- Monthly copy/paste, aggregation, and chart updates are repetitive.
- Excluded rows are difficult to trace after the report is produced.

After:

- Convert each configured source schema into one canonical format.
- Reconcile every input row as accepted, duplicate, or rejected.
- Aggregate sales, orders, units, and month-over-month movement automatically.
- Produce normalized CSV and auditable JSON outputs; the development workflow also builds Excel demonstrations.
- Preserve source filename, source row number, and input SHA-256 lineage.

## Documents

- [`docs/01_product_brief.md`](docs/01_product_brief.md) — canonical v1 scope
- [`docs/04_implementation_gate.md`](docs/04_implementation_gate.md) — implementation decision and conditions
- [`docs/05_data_contract.md`](docs/05_data_contract.md) — source and output contracts
- [`docs/08_compatibility_report.md`](docs/08_compatibility_report.md) — office-suite compatibility
- [`docs/10_distribution_decision.md`](docs/10_distribution_decision.md) — public distribution model
- [`docs/12_bilingual_strategy.md`](docs/12_bilingual_strategy.md) — Japanese/English presentation strategy
- [`docs/14_release_readiness.md`](docs/14_release_readiness.md) — local release package and publication boundary

## Run the portable sample

Python 3.11+ is required. The portable pipeline has no third-party runtime dependencies.

Install the command in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

```bash
./scripts/run_portable_sample.sh
```

### Direct command

The validation and aggregation pipeline uses only the Python standard library and can run without the workbook runtime:

```bash
PYTHONPATH=src python3 -m ec_sales.cli \
  --input sample_data/input \
  --output output \
  --contract config/source_contracts.json
```

Generated files are written to `output/`:

- `clean_data.csv`
- `quality_report.json`
- `report_model.json`

The Excel workbook is created only by the development workflow described below.

Run the dependency-free Python tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Sample reconciliation

| Measure | Result |
|---|---:|
| Input rows | 12 |
| Accepted rows | 10 |
| Excluded duplicate rows | 1 |
| Rejected rows | 1 |
| Net sales | ¥36,590 |
| Completed orders | 8 |

The totals above are fixture expectations verified by automated tests. The sample intentionally contains one exact duplicate, one cancelled order, one refund, and one malformed quantity.

## Architecture

```text
Configured source adapters
          ↓
CSV validation and sensitive-column guard
          ↓
Canonical rows with source lineage
          ↓
Duplicate handling and row reconciliation
          ↓
Deterministic sales aggregates
          ↓
CSV + JSON + Excel report
```

## Limitations

- v1 accepts only the three documented fictional schemas.
- All values use JPY; currency conversion is out of scope.
- The project does not provide accounting or tax advice.
- The workbook builder currently depends on the Codex bundled spreadsheet runtime. The Python CSV/JSON outputs are portable, while the verified workbook is a demonstration artifact.
- Portfolio development uses synthetic data only. Do not add customer or employer data.

## License

Project-authored source and documentation are available under the MIT License. Third-party components retain their respective licenses.

## Development workbook workflow

`scripts/run_sample.sh` generates the Excel workbook only inside the configured Codex spreadsheet development environment. It is intentionally separate from the portable public command.

## Notice

The Prior Art/IP review in this repository is an initial risk screen, not legal advice or a freedom-to-operate opinion.
