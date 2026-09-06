#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="${1:-$project_dir/output}"
locale="${2:-en}"

PYTHONPATH="$project_dir/src" python3 -m ec_sales.cli \
  --input "$project_dir/sample_data/input" \
  --output "$output_dir" \
  --contract "$project_dir/config/source_contracts.json"

node "$project_dir/scripts/build_report.mjs" \
  --model "$output_dir/report_model.json" \
  --locale "$locale" \
  --output "$output_dir/ec_sales_report_${locale}.xlsx"

echo "Created $output_dir/ec_sales_report_${locale}.xlsx"
