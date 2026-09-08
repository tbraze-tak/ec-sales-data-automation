# Product brief — EC Sales Data Automation

Status: canonical for v1 planning
Date: 2026-09-06

## Current v0.1 authority

The formal specification in `16_csv_data_bridge_formal_spec_v0.1.md` governs the current CSV Data Bridge v0.1 implementation. If the legacy v1 planning terminology below conflicts with that specification, the v0.1 formal specification takes precedence.

## CSV Data Bridge MVP elevation

The current product target is a Japanese-first local Streamlit application. A user uploads multiple supported CSV files, selects one or more outputs, converts them, and downloads either one file or a ZIP. Required outputs are canonical Clean CSV, a formula-linked Excel sales report, and a wholly fictional Accounting System DEMO CSV.

The existing deterministic pipeline remains the Data Bridge Core. The UI, input detection, and output adapters must remain separate from that core. The sample dataset must contain at least 500 wholly synthetic rows across approximately twelve months, three fictional stores, and 20–30 fictional products.

Workbook aggregates must be traceable to `Clean_Data`. Dashboard net sales must equal Monthly, Channel, Product, and Clean_Data net sales. Unknown CSV layouts and malformed rows must produce understandable user-facing results without exposing a Python traceback.

## Problem

Small EC operators often receive sales exports from multiple channels with incompatible columns, date formats, status names, tax/shipping representation, and encodings. Repeating the cleanup and monthly summary by hand is slow and error-prone.

## User and outcome

The primary user is a small-business operator or back-office worker who is comfortable placing files in a folder but does not want to maintain formulas or write code.

The desired outcome is a reproducible Excel report produced from source CSVs with an audit-friendly record of accepted files, rejected rows, transformations, and summary calculations.

## v1 input

Three fictional sales channels, deliberately not named after or presented as real marketplaces:

- `North Market`
- `Sakura Mall`
- `Harbor Shop`

Each channel has a documented adapter. Sample CSVs are wholly synthetic and created in this repository. v1 does not connect to external accounts or APIs.

## Canonical normalized fields

- `source_channel`
- `source_file`
- `source_row`
- `order_id`
- `order_date`
- `order_status`
- `product_id`
- `product_name`
- `quantity`
- `unit_price`
- `discount_amount`
- `shipping_amount`
- `tax_amount`
- `gross_sales`
- `net_sales`
- `currency`

The exact formulas and refund treatment must be fixed in a data contract before coding. Monetary values use decimal arithmetic, never binary floating point.

## v1 outputs

An `.xlsx` workbook with:

- `Summary`: total net sales, order count, units, average order value, month-over-month change
- `Monthly`: monthly values and trend chart
- `By_Channel`: channel comparison and chart
- `By_Product`: product ranking and top-products chart
- `Clean_Data`: normalized accepted rows
- `Data_Quality`: file/row counts, validation failures, duplicates, and exclusions
- `Run_Info`: execution time, tool version, input hashes, and configuration identifier

The tool also writes a machine-readable validation report and returns a non-zero exit code on fatal schema errors.

## Out of scope for v1

- Marketplace APIs, scraping, login automation, cloud upload, or scheduled execution
- Inventory, ads, fulfillment, CRM, accounting journal entries, and tax filing
- Currency conversion and multi-currency consolidation
- GUI or hosted SaaS
- Probabilistic/AI-based schema guessing
- Macros/VBA
- Processing any real customer or employer data during portfolio development

## Success criteria

- A first-time user can follow the README and generate the sample report with one command.
- Three intentionally different synthetic schemas normalize into the canonical schema.
- Accepted and rejected row counts reconcile with every input row.
- Aggregates reconcile to fixture expectations exactly.
- Re-running the same inputs and configuration produces the same tabular results.
- The workbook opens without repair warnings in LibreOffice; Excel compatibility is structurally tested, with real Microsoft Excel verification deferred until an environment is available.
- No identifier, file, module, sample, or documentation references employer systems or work domains.

## Portfolio message

Show the business outcome: recurring manual CSV consolidation becomes a repeatable, auditable workflow. The portfolio should not claim unique algorithms, marketplace affiliation, or production readiness for arbitrary customer data.
