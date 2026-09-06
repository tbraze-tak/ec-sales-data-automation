from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from ec_sales.bridge import accounting_demo_bytes, clean_csv_bytes, identify_csv, process_uploads, zip_outputs
from ec_sales.output_adapters import build_excel_report
from ec_sales.pipeline import PipelineError


ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT / "config" / "source_contracts.json"
SAMPLE_DIR = ROOT / "sample_data" / "input"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("csv-data-bridge")

st.set_page_config(page_title="CSV Data Bridge", page_icon="📄", layout="centered")
st.title("CSV Data Bridge")
st.caption("複数のCSVを、必要な業務形式へまとめて変換")

uploaded = st.file_uploader("CSVファイルをここへドロップしてください", type=["csv"], accept_multiple_files=True)
use_sample = st.checkbox("サンプルデータを使う（1,000件以上）")
files = (
    [(path.name, path.read_bytes()) for path in sorted(SAMPLE_DIR.glob("*.csv"))]
    if use_sample else [(item.name, item.getvalue()) for item in uploaded or []]
)

recognized: list[tuple[str, bytes]] = []
if files:
    st.subheader("読み込みファイル")
    for name, data in files:
        try:
            detected = identify_csv(data, name, CONTRACT)
            recognized.append((name, data))
            st.success(f'{name} → {detected["source_name"]}形式 → {detected["rows"]:,} rows')
        except PipelineError as exc:
            st.error(f"{name} → 形式を判定できませんでした")
            logger.warning("Could not identify %s: %s", name, exc)

choices = st.multiselect(
    "出力形式を選択",
    ["統合・クリーンCSV", "Excel売上レポート", "会計システム取込形式（DEMO）"],
    default=["統合・クリーンCSV", "Excel売上レポート"],
)
st.caption("会計システム取込形式はDEMOです。実案件ではお客様の取込仕様に合わせてカスタマイズします。")

if st.button("変換する", type="primary", disabled=not recognized or not choices):
    try:
        model = process_uploads(recognized, CONTRACT)
        quality = model["quality"]
        col1, col2, col3 = st.columns(3)
        col1.metric("正常", f'{quality["accepted_rows"]:,}件')
        col2.metric("要確認", f'{quality["rejected_rows"]:,}件')
        col3.metric("除外", f'{quality["excluded_duplicate_rows"]:,}件')
        if quality["fatal_files"]:
            st.warning(f'{len(quality["fatal_files"])}ファイルを処理できませんでした。列構成または文字コードを確認してください。')

        outputs: dict[str, bytes] = {}
        if "統合・クリーンCSV" in choices:
            outputs["clean_sales_data.csv"] = clean_csv_bytes(model)
        if "Excel売上レポート" in choices:
            outputs["sales_report.xlsx"] = build_excel_report(model)
        if "会計システム取込形式（DEMO）" in choices:
            outputs["accounting_import_demo.csv"] = accounting_demo_bytes(model)
        if len(outputs) == 1:
            name, data = next(iter(outputs.items()))
            st.download_button("ファイルをダウンロード", data=data, file_name=name)
        else:
            st.download_button("ZIPをダウンロード", data=zip_outputs(outputs), file_name="csv_data_bridge_output.zip", mime="application/zip")
    except Exception as exc:
        logger.exception("Conversion failed: %s", exc)
        st.error("変換できませんでした。CSVの文字コードまたは列構成を確認してください。")
