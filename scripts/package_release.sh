#!/usr/bin/env bash
set -euo pipefail

version=0.1.0
source_root=${1:-outputs/csv-data-bridge-mvp}
release_root="outputs/release/csv-data-bridge-v${version}"
artifacts=(clean_sales_data.csv sales_report.xlsx accounting_import_demo.csv csv_data_bridge_output.zip)

for artifact in "${artifacts[@]}"; do
  if [[ ! -f "$source_root/$artifact" ]]; then
    echo "Artifact not found: $source_root/$artifact" >&2
    exit 1
  fi
done

rm -rf "$release_root"
mkdir -p "$release_root"
for artifact in "${artifacts[@]}"; do
  cp "$source_root/$artifact" "$release_root/$artifact"
done
cp "RELEASE_NOTES_v${version}.md" "$release_root/"

(
  cd "$release_root"
  shasum -a 256 "${artifacts[@]}" > SHA256SUMS.txt
  shasum -a 256 -c SHA256SUMS.txt
)

echo "Release package prepared: $release_root"
