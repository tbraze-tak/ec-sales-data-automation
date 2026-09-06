# Data contract v1.0.0

## Input discovery

Only files matching a configured source pattern are processed. Each file must match exactly one adapter. Files matching no adapter or multiple adapters are fatal input errors.

An adapter declares its encoding, accepted date formats, required source columns, column mapping, and status mapping in `config/source_contracts.json`.

## Canonical values

- All v1 monetary amounts are integer JPY values parsed with `Decimal` and must not contain fractional yen.
- Dates are normalized to `YYYY-MM-DD` in Asia/Tokyo.
- Quantities are positive integers in source rows.
- Blank optional monetary fields mean zero.
- Unknown status values are rejected.
- Unexpected columns matching sensitive-field indicators such as name, address, email, phone, card, payment token, or Japanese equivalents cause the entire file to fail closed.

## Calculations

For completed rows:

```text
gross_sales = quantity × unit_price
net_sales   = gross_sales - discount_amount + shipping_amount + tax_amount
```

Cancelled rows remain in `Clean_Data` with `gross_sales = 0` and `net_sales = 0`.

Refund rows are stored as negative transactions. Quantity and all nonzero monetary components are negated before calculation. A source refund therefore uses ordinary positive magnitudes.

## Duplicate policy

The v1 identity is:

```text
source_channel + order_id + product_id + normalized status
```

- Byte-for-byte equivalent normalized rows after the first are excluded as duplicates.
- Rows with the same identity but conflicting values are rejected as `duplicate_conflict`.
- The pipeline never silently chooses between conflicting rows.

## Reconciliation invariant

For every run:

```text
input_rows = accepted_rows + excluded_duplicate_rows + rejected_rows
```

Fatal file errors are reported separately because their rows may not be safely parseable.

## Output contract

- `clean_data.csv`: normalized accepted rows including source lineage.
- `quality_report.json`: file and row reconciliation plus each rejection reason.
- `report_model.json`: deterministic KPI and aggregation model used by the workbook builder.
- `ec_sales_report.xlsx`: reader-facing report generated from the report model and clean data.

## CSV Data Bridge presentation contract

The downloadable Clean CSV uses these stable columns:

`store`, `order_id`, `order_date`, `year_month`, `status`, `sku`, `product_name`, `quantity`, `unit_price`, `gross_sales`, `discount`, `shipping`, `tax`, `net_sales`, `source_file`.

Input layout detection uses the configured required-column sets. Detection must resolve to exactly one adapter. Filenames are informative but are not required for browser uploads.

The Excel report contains `Dashboard`, `Monthly`, `Channel`, `Product`, `Clean_Data`, `Data_Quality`, and `README`. Aggregate and Dashboard values are formulas referencing `Clean_Data` or a directly dependent aggregate sheet.
