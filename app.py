from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from ec_sales.bridge import (
    accounting_demo_bytes,
    clean_csv_bytes,
    identify_csv,
    process_uploads,
    zip_outputs,
)
from ec_sales.output_adapters import build_excel_report
from ec_sales.pipeline import PipelineError


ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT / "config" / "source_contracts.json"
SAMPLE_DIR = ROOT / "sample_data" / "input"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("csv-data-bridge")


# ------------------------------------------------------------
# 表示文言
# ------------------------------------------------------------

LANGUAGE_CODES = {"日本語": "ja", "English": "en"}

STORE_NAMES = {
    "ja": {
        "north_market_2026.csv": "North Market 売上表",
        "sakura_mall_2026.csv": "Sakura Mall 売上表",
        "harbor_shop_2026.csv": "Harbor Shop 売上表",
    },
    "en": {
        "north_market_2026.csv": "North Market sales CSV",
        "sakura_mall_2026.csv": "Sakura Mall sales CSV",
        "harbor_shop_2026.csv": "Harbor Shop sales CSV",
    },
}

OUTPUT_DESCRIPTIONS = {
    "ja": {
        "clean_sales_data.csv": "3店舗の売上データを共通形式へ変換し、1つに統合したCSVです。",
        "sales_report.xlsx": "統合データから月別・店舗別・商品別・税区分別の集計を作成したExcelレポートです。",
        "accounting_import_demo.csv": "別システムへデータを渡す場合の変換例です（DEMO形式）。",
    },
    "en": {
        "clean_sales_data.csv": "A single clean CSV that standardizes and combines sales data from all three stores.",
        "sales_report.xlsx": "An Excel report with automated monthly, store, product, and tax summaries.",
        "accounting_import_demo.csv": "A demonstration output showing how data can be mapped for another system (DEMO only).",
    },
}

UI_TEXT = {
    "ja": {
        "page_title": "複数店舗の売上データを一括集計",
        "product_caption": "CSV Data Bridge — 売上CSV自動変換デモ",
        "intro": "店舗ごとにバラバラな売上CSVを、自動でひとつの形式に整理します。",
        "source_heading": "3店舗の異なるCSV",
        "bridge_info": "**CSV Data Bridge**  \n登録された入力形式を自動判別し、データを統合します。",
        "outputs_intro": "**作成されるファイル**\n\n- ✓ Clean CSV\n- ✓ Excel売上レポート\n- ✓ 会計システム取込CSV（DEMO）",
        "try_heading": "では、実際にやってみましょう",
        "try_button": "デモを試してみる",
        "sample_heading": "サンプルCSVを確認したい方",
        "sample_caption": "このデモで使用する完全架空データです。",
        "source_download": "元CSVをダウンロード",
        "back": "← 戻る",
        "demo_title": "3店舗の売上データをまとめてみましょう",
        "demo_caption": "CSV Data Bridge — 操作デモ",
        "load_heading": "1. 売上データを読み込む",
        "load_button": "3店舗のサンプル売上データを読み込む",
        "table_store": "売上表",
        "table_file": "ファイル",
        "table_rows": "件数",
        "row_count": "{count:,}件",
        "recognition_error": "{store} を認識できませんでした。",
        "loaded": "{stores}店舗・{rows:,}件の売上データを読み込みました",
        "select_heading": "2. 作成するファイルを選ぶ",
        "clean_label": "統合・クリーンCSV",
        "clean_caption": "3店舗の売上データを共通形式にそろえ、1つのCSVに統合します。",
        "excel_label": "Excel売上レポート",
        "excel_caption": "Dashboard・月別・店舗別・商品別・税区分別の集計を自動作成します。",
        "accounting_label": "会計システム取込CSV（DEMO）",
        "accounting_caption": "別システムへ取り込むための形式変換例です。",
        "accounting_notice": "※ 会計システム取込CSVはDEMO形式です。実在する会計ソフトへの対応を保証するものではありません。",
        "convert_heading": "3. 一括変換する",
        "load_first": "先に3店舗のサンプル売上データを読み込んでください。",
        "select_first": "作成するファイルを1つ以上選択してください。",
        "convert_button": "3店舗の売上データを一括変換",
        "processing": "売上データを確認・変換しています...",
        "complete": "✓ 変換が完了しました",
        "result_heading": "処理結果",
        "input_rows": "**入力データ：{rows:,}件**",
        "accepted": "✓ 正常",
        "review": "⚠ 要確認",
        "excluded": "✕ 除外",
        "metric_count": "{count:,}件",
        "fatal_files": "{count}ファイルを処理できませんでした。",
        "created_heading": "作成したファイル",
        "download_one": "作成したファイルをダウンロード",
        "download_many": "{count}ファイルをまとめてダウンロード",
        "conversion_error": "変換処理でエラーが発生しました。サンプルデータまたは変換設定を確認してください。",
    },
    "en": {
        "page_title": "Consolidate Sales Data from Multiple Stores",
        "product_caption": "CSV Data Bridge — Sales CSV Automation Demo",
        "intro": "Standardize different store sales CSVs and combine them into one clean dataset automatically.",
        "source_heading": "Three stores, three different CSV formats",
        "bridge_info": "**CSV Data Bridge**  \nAutomatically identifies configured input formats and consolidates the data.",
        "outputs_intro": "**Generated files**\n\n- ✓ Clean CSV\n- ✓ Excel sales report\n- ✓ Accounting import CSV (DEMO)",
        "try_heading": "Try the working demo",
        "try_button": "Start the demo",
        "sample_heading": "Download the sample CSVs",
        "sample_caption": "All data used in this demo is entirely fictional.",
        "source_download": "Download source CSV",
        "back": "← Back",
        "demo_title": "Combine Sales Data from Three Stores",
        "demo_caption": "CSV Data Bridge — Interactive Demo",
        "load_heading": "1. Load sales data",
        "load_button": "Load sample sales data from three stores",
        "table_store": "Sales source",
        "table_file": "File",
        "table_rows": "Rows",
        "row_count": "{count:,}",
        "recognition_error": "Could not recognize {store}.",
        "loaded": "Loaded {rows:,} sales rows from {stores} stores",
        "select_heading": "2. Select output files",
        "clean_label": "Combined clean CSV",
        "clean_caption": "Standardizes and combines sales data from all three stores into one CSV.",
        "excel_label": "Excel sales report",
        "excel_caption": "Automatically builds dashboard, monthly, store, product, and tax summaries.",
        "accounting_label": "Accounting import CSV (DEMO)",
        "accounting_caption": "A demonstration of mapping the processed data for another system.",
        "accounting_notice": "The accounting import CSV is a DEMO output only. It does not claim compatibility with any real accounting software.",
        "convert_heading": "3. Process all files",
        "load_first": "Load the sample sales data from three stores first.",
        "select_first": "Select at least one output file.",
        "convert_button": "Process sales data from all three stores",
        "processing": "Validating, standardizing, and processing sales data...",
        "complete": "✓ Processing complete",
        "result_heading": "Processing results",
        "input_rows": "**Input data: {rows:,} rows**",
        "accepted": "✓ Accepted",
        "review": "⚠ Review",
        "excluded": "✕ Excluded",
        "metric_count": "{count:,}",
        "fatal_files": "Could not process {count} file(s).",
        "created_heading": "Generated files",
        "download_one": "Download generated file",
        "download_many": "Download all {count} files",
        "conversion_error": "The conversion failed. Check the sample data or conversion configuration.",
    },
}

# ------------------------------------------------------------
# ページ設定
# ------------------------------------------------------------

initial_language = LANGUAGE_CODES.get(st.session_state.get("language", "日本語"), "ja")

st.set_page_config(
    page_title=UI_TEXT[initial_language]["page_title"],
    page_icon="📊",
    layout="centered",
)

language_label = st.radio(
    "Language",
    list(LANGUAGE_CODES),
    horizontal=True,
    key="language",
)
language = LANGUAGE_CODES[language_label]
copy = UI_TEXT[language]
store_names = STORE_NAMES[language]
output_descriptions = OUTPUT_DESCRIPTIONS[language]

if "page" not in st.session_state:
    st.session_state.page = "intro"

if "sample_loaded" not in st.session_state:
    st.session_state.sample_loaded = False

# ============================================================
# 画面1：説明
# ============================================================

if st.session_state.page == "intro":
    st.title(copy["page_title"])
    st.caption(copy["product_caption"])
    st.write(copy["intro"])

    st.subheader(copy["source_heading"])
    north, sakura, harbor = st.columns(3)
    north.markdown("**North Market**  \n`order_date / status / qty`")
    sakura.markdown("**Sakura Mall**  \n`注文日 / 状態 / 個数`")
    harbor.markdown("**Harbor Shop**  \n`created_at / state / units`")

    st.markdown("### ↓")
    st.info(copy["bridge_info"])
    st.markdown("### ↓")
    st.markdown(copy["outputs_intro"])

    st.markdown(f'## {copy["try_heading"]}')
    if st.button(
        copy["try_button"],
        type="primary",
        width="stretch",
    ):
        st.session_state.page = "demo"
        st.rerun()

    st.divider()
    st.subheader(copy["sample_heading"])
    st.caption(copy["sample_caption"])
    download_columns = st.columns(3)
    for column, sample_path in zip(download_columns, sorted(SAMPLE_DIR.glob("*.csv"))):
        with column:
            st.markdown(f"**{store_names.get(sample_path.name, sample_path.name)}**")
            st.download_button(
                copy["source_download"],
                data=sample_path.read_bytes(),
                file_name=sample_path.name,
                mime="text/csv",
                key=f"download_{sample_path.name}",
                width="stretch",
            )


# ============================================================
# 画面2：操作
# ============================================================

elif st.session_state.page == "demo":

    col_back, col_title = st.columns([1, 4])

    with col_back:
        if st.button(copy["back"]):
            st.session_state.page = "intro"
            st.rerun()

    st.title(copy["demo_title"])
    st.caption(copy["demo_caption"])

    # --------------------------------------------------------
    # 1. 読み込み
    # --------------------------------------------------------

    st.subheader(copy["load_heading"])

    if st.button(
        copy["load_button"],
        type="primary",
        width="stretch",
    ):
        st.session_state.sample_loaded = True

    files: list[tuple[str, bytes]] = []

    if st.session_state.sample_loaded:
        files = [
            (path.name, path.read_bytes())
            for path in sorted(SAMPLE_DIR.glob("*.csv"))
        ]

    recognized: list[tuple[str, bytes]] = []

    if files:
        display_rows = []

        for name, data in files:
            try:
                detected = identify_csv(data, name, CONTRACT)
                recognized.append((name, data))

                display_rows.append(
                    {
                        copy["table_store"]: store_names.get(name, name),
                        copy["table_file"]: name,
                        copy["table_rows"]: copy["row_count"].format(count=detected["rows"]),
                    }
                )

            except PipelineError as exc:
                st.error(copy["recognition_error"].format(store=store_names.get(name, name)))
                logger.warning("Could not identify %s: %s", name, exc)

        if recognized:
            total_input_rows = sum(
                identify_csv(data, name, CONTRACT)["rows"]
                for name, data in recognized
            )

            st.success(copy["loaded"].format(stores=len(recognized), rows=total_input_rows))

            st.table(display_rows)

    st.divider()

    # --------------------------------------------------------
    # 2. 出力選択
    # --------------------------------------------------------

    st.subheader(copy["select_heading"])

    clean_selected = st.checkbox(
        copy["clean_label"],
        value=True,
        key="clean_selected",
    )
    st.caption(copy["clean_caption"])

    excel_selected = st.checkbox(
        copy["excel_label"],
        value=True,
        key="excel_selected",
    )
    st.caption(copy["excel_caption"])

    accounting_selected = st.checkbox(
        copy["accounting_label"],
        value=False,
        key="accounting_selected",
    )
    st.caption(copy["accounting_caption"])

    st.caption(copy["accounting_notice"])

    choices: list[str] = []

    if clean_selected:
        choices.append("clean_csv")

    if excel_selected:
        choices.append("excel_report")

    if accounting_selected:
        choices.append("accounting_demo")

    st.divider()

    # --------------------------------------------------------
    # 3. 変換
    # --------------------------------------------------------

    st.subheader(copy["convert_heading"])

    if not recognized:
        st.caption(copy["load_first"])

    elif not choices:
        st.caption(copy["select_first"])

    convert_clicked = st.button(
        copy["convert_button"],
        type="primary",
        disabled=not recognized or not choices,
        width="stretch",
    )

    if convert_clicked:
        try:
            with st.spinner(copy["processing"]):
                model = process_uploads(recognized, CONTRACT)
                quality = model["quality"]

                outputs: dict[str, bytes] = {}

                if clean_selected:
                    outputs["clean_sales_data.csv"] = clean_csv_bytes(model)

                if excel_selected:
                    outputs["sales_report.xlsx"] = build_excel_report(model)

                if accounting_selected:
                    outputs["accounting_import_demo.csv"] = accounting_demo_bytes(model)

            st.success(copy["complete"])

            st.subheader(copy["result_heading"])

            input_rows = (
                quality["accepted_rows"]
                + quality["rejected_rows"]
                + quality["excluded_duplicate_rows"]
            )

            st.write(copy["input_rows"].format(rows=input_rows))

            col1, col2, col3 = st.columns(3)

            col1.metric(
                copy["accepted"],
                copy["metric_count"].format(count=quality["accepted_rows"]),
            )

            col2.metric(
                copy["review"],
                copy["metric_count"].format(count=quality["rejected_rows"]),
            )

            col3.metric(
                copy["excluded"],
                copy["metric_count"].format(count=quality["excluded_duplicate_rows"]),
            )

            if quality["fatal_files"]:
                st.warning(copy["fatal_files"].format(count=len(quality["fatal_files"])))

            st.subheader(copy["created_heading"])

            for name in outputs:
                st.markdown(
                    f"**✓ `{name}`**  \n"
                    f"{output_descriptions.get(name, '')}"
                )

            if len(outputs) == 1:
                name, data = next(iter(outputs.items()))

                st.download_button(
                    copy["download_one"],
                    data=data,
                    file_name=name,
                    width="stretch",
                )

            else:
                st.download_button(
                    copy["download_many"].format(count=len(outputs)),
                    data=zip_outputs(outputs),
                    file_name="csv_data_bridge_output.zip",
                    mime="application/zip",
                    width="stretch",
                )

        except Exception as exc:
            logger.exception("Conversion failed: %s", exc)

            st.error(copy["conversion_error"])
