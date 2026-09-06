# Phase 27 release readiness

Date: 2026-09-06
Target version: `v0.1.0`

## Local preparation completed

- Added public package metadata and a changelog.
- Prepared concise release notes describing scope, evidence, attachments, and limitations.
- Added a deterministic packaging script for the Japanese and English workbooks.
- Added SHA-256 checksum generation and verification to the package workflow.
- Kept all release packages and generated workbooks outside Git history.
- Re-ran tests, clean installation, repository scanning, and Git-history scanning.

## Suggested GitHub metadata

Description:

> Normalize incompatible EC sales CSVs into auditable CSV/JSON outputs and bilingual Excel report samples using wholly synthetic data.

Topics:

`python`, `ecommerce`, `csv`, `data-cleaning`, `etl`, `sales-reporting`, `excel`, `portfolio-project`, `synthetic-data`

## Publication boundary

The repository remains local. Creating a remote, pushing commits, making the repository public, creating a tag or release, and uploading attachments all require explicit user direction.

## Expected release package

```text
ec-sales-data-automation-v0.1.0/
├── RELEASE_NOTES_v0.1.0.md
├── SHA256SUMS.txt
├── ec_sales_report_en.xlsx
└── ec_sales_report_ja.xlsx
```

The package is locally reproducible with:

```bash
./scripts/package_release.sh \
  outputs/.../ec_sales_report_en.xlsx \
  outputs/.../ec_sales_report_ja.xlsx
```
