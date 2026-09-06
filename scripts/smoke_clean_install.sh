#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
smoke_root="$(mktemp -d /tmp/ec-sales-clean.XXXXXX)"
trap 'rm -rf "$smoke_root"' EXIT

cp -R "$project_dir" "$smoke_root/project"
rm -rf "$smoke_root/project/.git" "$smoke_root/project/.venv" "$smoke_root/project/node_modules" "$smoke_root/project/output" "$smoke_root/project/outputs"

python3 -m venv "$smoke_root/venv"
"$smoke_root/venv/bin/python" -m pip install --no-deps "$smoke_root/project"

cd "$smoke_root/project"
"$smoke_root/venv/bin/ec-sales" \
  --input sample_data/input \
  --output smoke-output \
  --contract config/source_contracts.json

"$smoke_root/venv/bin/python" -c 'import json; from pathlib import Path; p=Path("smoke-output"); q=json.loads((p/"quality_report.json").read_text()); m=json.loads((p/"report_model.json").read_text()); assert q["reconciliation_ok"] and q["input_rows"] == 12 and m["kpis"]["net_sales"] == 36590 and (p/"clean_data.csv").is_file(); print("Clean-install smoke test passed")'
