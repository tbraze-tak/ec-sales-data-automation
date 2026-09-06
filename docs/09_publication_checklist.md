# Portfolio publication checklist

## Repository hygiene

- [x] Dedicated repository
- [x] No remote configured during development
- [x] Employer and `argo-core` separation rule documented
- [x] Generated outputs and local runtimes ignored by Git
- [x] MIT license added for project-authored work
- [x] Data-safety policy added
- [x] Review staged files before the first commit
- [x] Confirm no existing commit history is present before the first commit
- [x] Add and run a complete committed-blob history scanner
- [ ] Run the complete Git-history scan again immediately before making the repository public

## Demonstration content

- [x] Fictional shop names
- [x] Fully synthetic CSV fixtures
- [x] Duplicate, cancellation, refund, and malformed-row examples
- [x] Before/After explanation
- [x] Japanese and English summary images
- [x] Japanese and English workbooks generated from one report model
- [x] Reconciliation totals documented
- [x] Local `v0.1.0` release bundle with SHA-256 checksums
- [ ] Add a short terminal demonstration or GIF if it improves the portfolio listing

## Engineering quality

- [x] Versioned data contract
- [x] Explicit source adapters
- [x] Deterministic outputs
- [x] Fifteen automated tests
- [x] LibreOffice compatibility check
- [x] Microsoft Excel for Mac smoke test
- [x] Separate the portable Python core from development-only workbook generation
- [x] Run installation and sample generation from an isolated clean copy
- [x] Add CI for Python 3.11–3.13
- [x] Add package metadata, changelog, and release notes
- [x] Streamlit clean-install and startup smoke test
- [x] Formula-linked Excel reconciliation across all aggregate sheets

## Claims and legal review

- [x] No claim of unique or patented technology
- [x] No third-party logos or marketplace affiliation claims
- [x] Prior Art and initial dependency-license review recorded
- [x] Limitations stated
- [x] Re-check current first-commit candidates for generated support files and third-party assets
- [ ] Re-check third-party notices if a public workbook backend is selected later

## Publication gate

Describe the Python CSV/JSON pipeline as portable. Describe the workbook as a verified demonstration artifact, not as an arbitrary-machine one-command output. Keep generated `.xlsx` files out of Git; provide Japanese and English versions as release attachments or direct portfolio samples.
