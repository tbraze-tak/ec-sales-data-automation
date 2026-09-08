# Repository working rules

## Scope

This repository is exclusively for the portfolio project “EC Sales Data Automation.”

## Isolation requirements

- Never read from, copy from, import from, modify, or commit changes to `argo-core` or any employer/work-related repository as part of implementation.
- Never use employer data, logs, documents, code, customer information, specifications, incidents, DBC files, or non-public know-how.
- Never use anonymized employer data. Test and demo data must be generated from scratch and be wholly synthetic.
- Do not implement features related to EVs, CAN, BMS, OBC, VCU, vehicle diagnosis, or charger analysis.
- Use fictional store and product names. Do not include third-party logos or imply affiliation with real marketplaces.

## Source of truth

- Current status and machine handoff: `docs/CURRENT_STATUS.md`
- Product scope: `docs/01_product_brief.md`
- Implementation decision and acceptance gates: `docs/04_implementation_gate.md`
- When scope changes, update those documents before implementation.

## Engineering expectations

- Prefer deterministic, configuration-driven transforms.
- Preserve source-row traceability without retaining real personal data.
- Reject ambiguous or invalid inputs explicitly; do not silently guess.
- Add tests for mappings, monetary calculations, dates, duplicates, refunds, and malformed files.
- Keep generated inputs and outputs reproducible.
