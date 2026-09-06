from __future__ import annotations

from pathlib import Path

from ec_sales.bridge import accounting_demo_bytes, clean_csv_bytes, zip_outputs
from ec_sales.output_adapters import build_excel_report
from ec_sales.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "csv-data-bridge-mvp"


def main() -> None:
    model = run_pipeline(ROOT / "sample_data" / "input", OUTPUT / "model", ROOT / "config" / "source_contracts.json")
    files = {
        "clean_sales_data.csv": clean_csv_bytes(model),
        "sales_report.xlsx": build_excel_report(model),
        "accounting_import_demo.csv": accounting_demo_bytes(model),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (OUTPUT / name).write_bytes(data)
    (OUTPUT / "csv_data_bridge_output.zip").write_bytes(zip_outputs(files))
    quality = model["quality"]
    print(
        f'Built demo: input={quality["input_rows"]}, accepted={quality["accepted_rows"]}, '
        f'duplicates={quality["excluded_duplicate_rows"]}, rejected={quality["rejected_rows"]}'
    )


if __name__ == "__main__":
    main()
