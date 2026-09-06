# Workbook compatibility report

Test date: 2026-09-06

## Artifact-level checks

- XLSX ZIP package integrity: no errors.
- Seven expected worksheets are present.
- Summary values reconcile to the tested report model.
- Three native charts are generated from worksheet ranges.
- Artifact-tool formula error scan: no matches.
- Every worksheet was rendered and visually reviewed.

## Application checks

| Application | Check | Result |
|---|---|---|
| LibreOffice | Headless open and PDF export | Pass — seven-page PDF created |
| Microsoft Excel for Mac | Open, read worksheet count, close without saving | Pass — seven worksheets read; workbook closed without saving |

LibreOffice emitted font-cache warnings in the sandbox but successfully opened and exported the workbook. No converted artifact is retained in the repository.

## Acceptance

Compatibility is accepted for a portfolio sample when the workbook opens without a repair prompt, contains seven worksheets, displays the summary values and charts, and can be exported from LibreOffice. Visual parity between applications is desirable but minor font and chart rendering differences are acceptable.

Result: accepted for the Phase 23 portfolio sample.
