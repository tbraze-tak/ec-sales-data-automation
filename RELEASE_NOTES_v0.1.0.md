# EC Sales Data Automation v0.1.0

The first portfolio release demonstrates how three incompatible, wholly synthetic EC sales exports can be validated, normalized, reconciled, and summarized through one deterministic pipeline.

## Included release attachments

- `ec_sales_report_ja.xlsx` — Japanese presentation workbook
- `ec_sales_report_en.xlsx` — English presentation workbook
- `SHA256SUMS.txt` — integrity hashes for both workbooks

Both workbooks contain the same figures and are generated from the same report model. The language selection changes presentation labels only.

## Verified sample result

- 12 input rows
- 10 accepted rows
- 1 excluded duplicate
- 1 rejected malformed row
- JPY 36,590 net sales
- 8 completed orders
- Reconciliation: OK

## Compatibility

Both workbooks were opened successfully in Microsoft Excel for Mac and LibreOffice. Each workbook contains seven worksheets.

## Important limitation

The Python CSV/JSON pipeline is portable. Workbook generation currently depends on the managed development runtime, so the attached workbooks are demonstration artifacts rather than proof of arbitrary-machine workbook generation.
