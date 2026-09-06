# CSV Data Bridge v0.1.0

The first portfolio release provides a Japanese-first local Streamlit app that validates, normalizes, reconciles, and converts three incompatible, wholly synthetic EC sales exports.

## Main workflow

1. Drop multiple CSV files or select the built-in sample.
2. Select Clean CSV, Excel report, Accounting DEMO, or all three.
3. Convert the data.
4. Download one file or one ZIP.

## Included release attachments

- `clean_sales_data.csv` — canonical UTF-8 BOM data
- `sales_report.xlsx` — formula-linked Japanese-first report
- `accounting_import_demo.csv` — fictional destination-format example
- `csv_data_bridge_output.zip` — the three outputs in one download
- `SHA256SUMS.txt` — integrity hashes for all outputs

## Verified sample result

- 1,024 input rows
- 1,022 accepted rows
- 1 excluded duplicate
- 1 rejected malformed row
- JPY 9,653,295 net sales
- 986 completed orders
- Reconciliation: OK

## Compatibility

The current workbook was recalculated successfully in LibreOffice and contains seven worksheets. Dashboard, Monthly, Channel, Product, and Clean_Data reconcile to the same total.

## Important limitation

Accounting System DEMO is fictional and is not compatible with any real accounting product. A real engagement requires a customer-specific output adapter.
