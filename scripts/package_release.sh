#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 EN_WORKBOOK JA_WORKBOOK" >&2
  exit 2
fi

english_workbook=$1
japanese_workbook=$2
version=0.1.0
release_root="outputs/release/ec-sales-data-automation-v${version}"

for workbook in "$english_workbook" "$japanese_workbook"; do
  if [[ ! -f "$workbook" ]]; then
    echo "Workbook not found: $workbook" >&2
    exit 1
  fi
done

rm -rf "$release_root"
mkdir -p "$release_root"
cp "$english_workbook" "$release_root/ec_sales_report_en.xlsx"
cp "$japanese_workbook" "$release_root/ec_sales_report_ja.xlsx"
cp "RELEASE_NOTES_v${version}.md" "$release_root/"

(
  cd "$release_root"
  shasum -a 256 ec_sales_report_en.xlsx ec_sales_report_ja.xlsx > SHA256SUMS.txt
  shasum -a 256 -c SHA256SUMS.txt
)

echo "Release package prepared: $release_root"
