#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="${1:-$project_dir/output}"

PYTHONPATH="$project_dir/src" python3 -m ec_sales \
  --input "$project_dir/sample_data/input" \
  --output "$output_dir" \
  --contract "$project_dir/config/source_contracts.json"

echo "Created portable CSV/JSON outputs in $output_dir"
