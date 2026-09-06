# Competitive and alternative analysis

Researched: 2026-09-06

## Market frame

This project enters a mature category. Combining files, transforming tabular data, calculating metrics, and creating charts are established capabilities. The portfolio value is therefore execution quality and a clear small-business workflow, not technical novelty.

## Direct alternatives

| Alternative | Existing strength | Gap/opportunity for this portfolio |
|---|---|---|
| Microsoft Power Query | Folder connector, repeatable transformations, Excel/Power BI integration | Microsoft's documented combine flow expects files to share the same structure. The proposed adapters intentionally normalize different shop schemas and expose validation/reconciliation. |
| Shopify Analytics | Native dashboard, sales reports, comparisons, exports | Strong inside one platform; this portfolio demonstrates cross-channel offline consolidation without account access. |
| Generic Python/pandas scripts | Flexible and inexpensive | Often delivered without a polished workbook, provenance, data-quality report, fixtures, or nontechnical instructions. |
| ETL/automation SaaS | Connectors, scheduling, hosted dashboards | Adds credentials, subscriptions, and setup. v1 is local, deterministic, and has no recurring service cost. |
| Manual Excel templates | Familiar and easy to inspect | Fragile when columns, encodings, refund rows, or date formats differ; manual steps are hard to reproduce. |

## Evidence

- Microsoft documents that Power Query can combine files from a folder, but its standard combine workflow assumes the files have the same type and structure: [Combine files overview](https://learn.microsoft.com/en-us/power-query/combine-files-overview).
- Shopify provides native analytics, customizable reports, tables/charts, and export to formats including CSV: [Shopify analytics](https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports) and [Exporting reports](https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports/report-types/custom-reports/export-reports).

## Positioning decision

Position v1 as a demonstrator of commissioned automation for messy multi-source exports:

> Different CSV layouts in, validated management workbook out — locally, repeatably, and with every excluded row explained.

Defensible differentiation for a portfolio:

- explicit per-source adapters rather than silent guessing;
- source-file and source-row lineage;
- reconciliation and visible data-quality reporting;
- deterministic synthetic fixtures and automated tests;
- a nontechnical one-command workflow;
- clean separation from third-party accounts and confidential data.

## Claims to avoid

- “Industry-first,” “patented,” “unique AI,” or “works with every marketplace.”
- Official compatibility with a marketplace unless tested against its current public export specification and permitted branding rules.
- Guaranteed accounting/tax accuracy.
- Fully automatic handling of unknown formats.

## Conclusion

There is enough portfolio value to proceed, but the implementation should emphasize reliability, explanation, and user experience. Competing feature-for-feature with Excel, Power BI, or a SaaS connector platform is not the v1 goal.
