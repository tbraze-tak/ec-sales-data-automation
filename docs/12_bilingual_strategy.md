# Bilingual portfolio strategy

Decision date: 2026-09-06

## Decision

Use one calculation pipeline and two presentation locales.

- Canonical field names and program identifiers remain in English.
- The Japanese workbook localizes sheet names, headings, fictional shop names, fictional product names, statuses, and quality messages.
- The English workbook keeps the original labels for overseas proposals.
- Both workbooks use the same `report_model.json`; therefore localization cannot change totals.
- `README.md` is the international entry point and `README.ja.md` is the Japanese client-facing explanation.

## Why

English identifiers are conventional for source code, configuration, and cross-border maintenance. Japanese-facing results reduce explanation time for domestic clients. Separate presentation outputs avoid mixing languages inside a client deliverable while preserving one tested implementation.

## Version-control policy

- Commit the summary images for both locales because they are small and useful on the repository front page.
- Keep generated workbooks out of Git history.
- Attach the Japanese and English `.xlsx` files to a tagged release or upload them directly as portfolio samples.
- Never maintain separate Japanese and English calculation code.

## Implementation status — 2026-09-13

- The Streamlit UI now provides a Japanese / English switch.
- The implementation retains one application and one calculation pipeline; locale selection is limited to the presentation layer.
- Locale selection does not change parsing, validation, aggregation, workbook generation, Accounting DEMO generation, output filenames, or result values.
- Automated tests pass 21/21, including the language-invariance test.
- Codex browser testing: PASS.
- Human Acceptance Test: PASS.
- Sakura Mall's Japanese source column names are intentionally retained as an example of an input schema; they are not untranslated UI text.
