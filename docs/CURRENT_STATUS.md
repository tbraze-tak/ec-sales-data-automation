# Mission 001 current status and MacBook handoff

Updated: 2026-09-13

Status: CSV Data Bridge and the Japanese / English UI switch are implemented and verified. The feature branch is pushed; integration into `main` is the next step.

## Mission 001

Portfolio #1「CSV Data Bridge」は、CrowdWorks等を通じて最初の副業収益を得るための公開Portfolioです。顧客向けタイトルは「複数店舗の売上データを一括集計」、プロダクト表記は「CSV Data Bridge — 売上CSV自動変換デモ」とします。

## Current Git and GitHub state

- Repository: `https://github.com/tbraze-tak/ec-sales-data-automation`
- GitHub default branch: `main`
- `origin/main` base: `5cf5d7a25470ed47c689d71352670b784914825b`
- Bilingual implementation branch: `codex/rev-002-bilingual-ui`
- Bilingual implementation commit: `273e3247e64ddcfddc6ce658fe9a0c86fd29c77c`
- The feature branch has been pushed to `origin/codex/rev-002-bilingual-ui`.
- `main` has not yet been changed by ARGO-REV-002.
- Current-machine worktree: `~/Documents/ChatGPT/ec-sales-data-automation-public`

The original worktree at `~/Documents/ChatGPT/ec-sales-data-automation` intentionally remains on `main@c8878fe` with an edited `app.py` and untracked `app_wip_before_spec.patch`. Do not modify, stash, reset, clean, delete, check out over, or copy files into that worktree.

## Completed functionality

- Three fictional store schemas (`North Market`, `Sakura Mall`, and `Harbor Shop`) are detected from their headers and converted into one canonical dataset.
- The pipeline validates rows, rejects ambiguous or malformed input, records source traceability, excludes exact duplicates, and handles cancellations and refunds deterministically.
- Outputs are a Clean CSV, an eight-sheet formula-linked Excel sales report, a clearly labelled fictional Accounting DEMO CSV, and a ZIP when multiple outputs are selected.
- One Streamlit application presents the same workflow in Japanese or English and provides downloadable synthetic samples.
- One calculation pipeline is shared by both languages. The switch changes presentation only: CSV processing, validation, aggregation, Excel generation, Accounting DEMO generation, output filenames, and result values are unchanged.
- Product tax rates come from an explicit synthetic product master. Normal sample rates are 10% and 8%; 1% appears only in the separate future test for April 2027 or later.

## Confirmed QA baseline

| Check | Confirmed result |
|---|---:|
| Input rows | 1,024 |
| Accepted rows | 1,022 |
| Review / rejected rows | 1 |
| Duplicate rows excluded | 1 |
| Product sales | JPY 8,781,775 |
| Refund product amount | JPY 87,325 |
| Net product sales | JPY 8,694,450 |
| Sales quantity | 2,955 |
| Refund quantity | 28 |
| Net quantity | 2,927 |
| Completed orders | 986 |
| Total billed | JPY 9,619,580 |
| Consumption tax | JPY 835,730 |

- Monthly, Store, Product, and Tax totals reconcile to Dashboard.
- Excel contains `Dashboard`, `Monthly`, `Store`, `Product`, `Tax`, `Clean_Data`, `Data_Quality`, and `README`.
- Excel formula errors: 0.
- Excel charts: 2.
- Formula references to `Clean_Data`: 328.
- Dashboard references to Store: 9.
- All eight sheets passed visual review.
- Microsoft Excel for Mac opened the workbook without a repair warning; both charts were visually confirmed.
- Automated tests: 21/21 passed (the existing 20 tests plus one language-invariance test).
- Python 3.11 `py_compile`: passed.
- Git publication security audit: 60 candidates passed.

### ARGO-REV-002 acceptance results

- Human Acceptance Test: PASS.
- Japanese mode and English mode both processed 1,024 input rows into 1,022 accepted rows, 1 review row, and 1 excluded duplicate.
- `clean_sales_data.csv`, `sales_report.xlsx`, and `accounting_import_demo.csv` were all generated successfully.
- Japanese and English modes produced identical processing results and output filenames.
- The Accounting CSV retains its required `DEMO` wording.

Do not repeat the full heavy QA only to resume work. Repeat affected checks when application code, calculations, data, workbook generation, or dependencies change.

## Open P1 improvement

### Sample data loading performance

During the Human Acceptance Test, loading the three sample-store CSV files felt slow. Loading completed normally, the main processing step remained fast, and the Portfolio is usable; this is not a blocker.

- Status: OPEN / non-blocking
- No performance change is included in ARGO-REV-002.
- Before a future fix, measure the loading path and identify the cause.

## Security and intellectual-property boundaries

- Use only wholly synthetic data created for this repository. Anonymized employer data is also prohibited.
- Do not use real company or customer data, employer data, internal logs, private specifications, DBC files, non-public information, source code, or know-how.
- Do not read from, copy from, import from, modify, or commit to `argo-core` or any employer/work-related repository.
- Do not add EV bus, CAN, BMS, OBC, VCU, vehicle-fault analysis, charger-analysis, or adjacent employer-domain features.
- Use only fictional store and product names. Do not use third-party logos or imply marketplace affiliation.
- Do not add API keys, tokens, credentials, personal information, or external-account access.

## Public wording rules

- Customer-facing title: 「複数店舗の売上データを一括集計」.
- Product name: 「CSV Data Bridge — 売上CSV自動変換デモ」.
- Accounting output must always say `DEMO`. Do not claim formal compatibility with any real accounting product.
- Normal tax-rate examples are 10% and 8%. The 1% case is only a future test for April 2027 or later.
- Do not use the ambiguous labels `net_sales` or 「純売上」.
- Primary KPIs are 商品売上、販売数量、返品数量、純販売数量、注文数、合計請求額.
- Supporting measures are 値引額、送料、消費税額. Use 返品商品金額 and 純商品売上 when explaining product-amount reconciliation.
- Claims must remain portfolio-scale and factual. Do not imply production readiness, patent clearance, tax advice, or official marketplace/accounting affiliation.

## What is settled and what remains undecided

Do not reconsider without a concrete defect or a scope change:

- the three fictional stores and synthetic dataset;
- deterministic, configuration-driven normalization and rejection policy;
- KPI definitions, refund signs, 10%/8% tax treatment, and the isolated future 1% test;
- the eight-sheet workbook structure and formula relationships;
- the completed QA baseline above;
- the one-application, one-calculation-pipeline architecture and presentation-only language switch;
- identical processing results and filenames across Japanese and English;
- repository isolation and publication boundaries.

Still undecided:

- the English Portfolio screenshot selection;
- the final Upwork Portfolio presentation and preview;
- the first application target and proposal content, subject to Human GO before submission.

## Remaining work and priority

### P0 — Revenue critical path

1. Integrate the feature branch into the GitHub source of truth.
2. Select the English Portfolio screenshots.
3. Complete the Upwork Portfolio.
4. Preview it.
5. Publish it.
6. Select the first application target.
7. Prepare the proposal.
8. Obtain Human GO.
9. Submit the application.

Do not place a full README rewrite on this critical path. Do not start Portfolio #2 or later work yet.

## Safe restart on the MacBook

If no clone exists:

```bash
git clone https://github.com/tbraze-tak/ec-sales-data-automation.git
cd ec-sales-data-automation
git remote -v
git status -sb
git log -5 --oneline --decorate
```

If a clone already exists, inspect before integrating anything:

```bash
cd /path/to/ec-sales-data-automation
git remote -v
git status -sb
git branch -vv
git fetch --prune origin
git log --oneline --decorate HEAD..origin/main
git log --oneline --decorate origin/main..HEAD
```

Do not begin with `git pull`, `git reset`, or an overwrite. If the existing clone is clean, on `main`, and has no local-only commits, update it with a fast-forward only:

```bash
git merge --ff-only origin/main
```

If the status is not clean or either comparison log shows local-only work, stop and inspect before changing the clone.

## Files Codex must read when resuming

Read these in order:

1. `AGENTS.md`
2. `README.ja.md` and `README.md`
3. `docs/CURRENT_STATUS.md`
4. `docs/16_csv_data_bridge_formal_spec_v0.1.md`
5. `docs/01_product_brief.md`
6. `docs/04_implementation_gate.md`
7. `docs/12_bilingual_strategy.md`
8. `docs/14_release_readiness.md`

Then ask Codex to continue from 「Portfolio公開準備の続き」. Keep Portfolio #2 out of scope.
