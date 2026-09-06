# Clean-install report

Test date: 2026-09-06
Platform: macOS, Python 3.12

## Procedure

`scripts/smoke_clean_install.sh` performed the following steps:

1. Created a new temporary directory.
2. Copied the project without Git metadata, local environments, Node modules, or generated outputs.
3. Created a new Python virtual environment.
4. Built and installed `ec-sales-data-automation` from `pyproject.toml`.
5. Ran the installed `ec-sales` console command against the synthetic sample inputs.
6. Verified row reconciliation, net sales, and all three portable output files.
7. Removed the temporary environment.

## Result

- Wheel build: pass
- Package installation: pass
- Console command: pass
- Input reconciliation: 12 = 10 accepted + 1 duplicate + 1 rejected
- Net sales: JPY 36,590
- `clean_data.csv`: present
- `quality_report.json`: present and reconciled
- `report_model.json`: present and correct

## Dependency note

The installed application has no third-party runtime dependencies. The Python packaging process downloads the declared setuptools build dependency when it is not already available. Workbook generation remains a separate development workflow.
