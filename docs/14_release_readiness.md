# Phase 27 release readiness

Date: 2026-09-06
Target version: `v0.1.0`

## Local preparation completed

- Added public package metadata and a changelog.
- Prepared concise release notes describing scope, evidence, attachments, and limitations.
- Added a deterministic packaging script for all CSV Data Bridge outputs.
- Added SHA-256 checksum generation and verification to the package workflow.
- Kept all release packages and generated workbooks outside Git history.
- Re-ran tests, clean installation, repository scanning, and Git-history scanning.

## Suggested GitHub metadata

Description:

> Drag, convert, and download incompatible EC sales CSVs as clean data, a formula-linked Excel report, or a fictional accounting format.

Topics:

`python`, `ecommerce`, `csv`, `data-cleaning`, `etl`, `sales-reporting`, `excel`, `portfolio-project`, `synthetic-data`

## Publication boundary

The repository remains local. Creating a remote, pushing commits, making the repository public, creating a tag or release, and uploading attachments all require explicit user direction.

## Expected release package

```text
csv-data-bridge-v0.1.0/
├── RELEASE_NOTES_v0.1.0.md
├── SHA256SUMS.txt
├── accounting_import_demo.csv
├── clean_sales_data.csv
├── csv_data_bridge_output.zip
└── sales_report.xlsx
```

The package is locally reproducible with:

```bash
PYTHONPATH=src python3 scripts/build_mvp_demo.py
./scripts/package_release.sh
```
