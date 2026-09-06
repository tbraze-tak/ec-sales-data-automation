# Repository baseline

Checked: 2026-09-06 (Asia/Tokyo)

## Initial state

The repository was initialized locally but contained no commits, branches beyond unborn `main`, remote, tracked files, application code, or project documentation.

Observed facts:

- Working directory: `ec-sales-data-automation`
- Git state: `No commits yet on main`
- Remote: none
- Existing source-of-truth file: none
- Existing implementation: none

The sibling directories `argo-core` and `argo-core 2` were inspected only at the repository-status/name level to confirm that they were not the source tree for this project. No file was changed in either directory.

## Recovered canonical intent

The prior project handoff in the Codex/ChatGPT task history defines Portfolio #1 as:

1. Generate wholly synthetic sales exports from several fictional EC shops with different schemas.
2. Import CSV files with Python.
3. Normalize column names and data representations.
4. Clean and merge the data.
5. Aggregate and analyze sales.
6. Generate an Excel report containing KPIs, tables, and charts.
7. Provide a folder-in / one-command / report-out workflow.

The handoff also explicitly prohibits reuse of employer information or work-product and requires separation from `argo-core` and work-related repositories.

## Canonicalization decision

Because the Git repository had no prior artifact, this repository now becomes the canonical implementation record. `docs/01_product_brief.md` is the product scope source of truth and `docs/04_implementation_gate.md` is the development-entry gate.

No external remote has been configured and no commit has been created in this phase.
