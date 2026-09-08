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
# 表示名
# ------------------------------------------------------------

STORE_NAMES = {
    "north_market_2026.csv": "North Market 売上表",
    "sakura_mall_2026.csv": "Sakura Mall 売上表",
    "harbor_shop_2026.csv": "Harbor Shop 売上表",
}

OUTPUT_DESCRIPTIONS = {
    "clean_sales_data.csv": "3店舗の売上データを共通形式へ変換し、1つに統合したCSVです。",
    "sales_report.xlsx": "統合データから月別・店舗別・商品別・税区分別の集計を作成したExcelレポートです。",
    "accounting_import_demo.csv": "別システムへデータを渡す場合の変換例です（DEMO形式）。",
}

# ------------------------------------------------------------
# ページ設定
# ------------------------------------------------------------

st.set_page_config(
    page_title="複数店舗の売上データを一括集計",
    page_icon="📊",
    layout="centered",
)

if "page" not in st.session_state:
    st.session_state.page = "intro"

if "sample_loaded" not in st.session_state:
    st.session_state.sample_loaded = False

# ============================================================
# 画面1：説明
# ============================================================

if st.session_state.page == "intro":
    st.title("複数店舗の売上データを一括集計")
    st.caption("CSV Data Bridge — 売上CSV自動変換デモ")
    st.write("店舗ごとにバラバラな売上CSVを、自動でひとつの形式に整理します。")

    st.subheader("3店舗の異なるCSV")
    north, sakura, harbor = st.columns(3)
    north.markdown("**North Market**  \n`order_date / status / qty`")
    sakura.markdown("**Sakura Mall**  \n`注文日 / 状態 / 個数`")
    harbor.markdown("**Harbor Shop**  \n`created_at / state / units`")

    st.markdown("### ↓")
    st.info("**CSV Data Bridge**  \n登録された入力形式を自動判別し、データを統合します。")
    st.markdown("### ↓")
    st.markdown(
        """
**作成されるファイル**

- ✓ Clean CSV
- ✓ Excel売上レポート
- ✓ 会計システム取込CSV（DEMO）
"""
    )

    st.markdown("## では、実際にやってみましょう")
    if st.button(
        "デモを試してみる",
        type="primary",
        width="stretch",
    ):
        st.session_state.page = "demo"
        st.rerun()

    st.divider()
    st.subheader("サンプルCSVを確認したい方")
    st.caption("このデモで使用する完全架空データです。")
    download_columns = st.columns(3)
    for column, sample_path in zip(download_columns, sorted(SAMPLE_DIR.glob("*.csv"))):
        with column:
            st.markdown(f"**{STORE_NAMES.get(sample_path.name, sample_path.name)}**")
            st.download_button(
                "元CSVをダウンロード",
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
        if st.button("← 戻る"):
            st.session_state.page = "intro"
            st.rerun()

    st.title("3店舗の売上データをまとめてみましょう")
    st.caption("CSV Data Bridge — 操作デモ")

    # --------------------------------------------------------
    # 1. 読み込み
    # --------------------------------------------------------

    st.subheader("1. 売上データを読み込む")

    if st.button(
        "3店舗のサンプル売上データを読み込む",
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
                        "売上表": STORE_NAMES.get(name, name),
                        "ファイル": name,
                        "件数": f'{detected["rows"]:,}件',
                    }
                )

            except PipelineError as exc:
                st.error(f"{STORE_NAMES.get(name, name)} を認識できませんでした。")
                logger.warning("Could not identify %s: %s", name, exc)

        if recognized:
            total_input_rows = sum(
                identify_csv(data, name, CONTRACT)["rows"]
                for name, data in recognized
            )

            st.success(
                f"{len(recognized)}店舗・{total_input_rows:,}件の売上データを読み込みました"
            )

            st.table(display_rows)

    st.divider()

    # --------------------------------------------------------
    # 2. 出力選択
    # --------------------------------------------------------

    st.subheader("2. 作成するファイルを選ぶ")

    clean_selected = st.checkbox(
        "統合・クリーンCSV",
        value=True,
    )
    st.caption("3店舗の売上データを共通形式にそろえ、1つのCSVに統合します。")

    excel_selected = st.checkbox(
        "Excel売上レポート",
        value=True,
    )
    st.caption("Dashboard・月別・店舗別・商品別・税区分別の集計を自動作成します。")

    accounting_selected = st.checkbox(
        "会計システム取込CSV（DEMO）",
        value=False,
    )
    st.caption("別システムへ取り込むための形式変換例です。")

    st.caption(
        "※ 会計システム取込CSVはDEMO形式です。"
        "実在する会計ソフトへの対応を保証するものではありません。"
    )

    choices: list[str] = []

    if clean_selected:
        choices.append("統合・クリーンCSV")

    if excel_selected:
        choices.append("Excel売上レポート")

    if accounting_selected:
        choices.append("会計システム取込形式（DEMO）")

    st.divider()

    # --------------------------------------------------------
    # 3. 変換
    # --------------------------------------------------------

    st.subheader("3. 一括変換する")

    if not recognized:
        st.caption("先に3店舗のサンプル売上データを読み込んでください。")

    elif not choices:
        st.caption("作成するファイルを1つ以上選択してください。")

    convert_clicked = st.button(
        "3店舗の売上データを一括変換",
        type="primary",
        disabled=not recognized or not choices,
        width="stretch",
    )

    if convert_clicked:
        try:
            with st.spinner("売上データを確認・変換しています..."):
                model = process_uploads(recognized, CONTRACT)
                quality = model["quality"]

                outputs: dict[str, bytes] = {}

                if clean_selected:
                    outputs["clean_sales_data.csv"] = clean_csv_bytes(model)

                if excel_selected:
                    outputs["sales_report.xlsx"] = build_excel_report(model)

                if accounting_selected:
                    outputs["accounting_import_demo.csv"] = accounting_demo_bytes(model)

            st.success("✓ 変換が完了しました")

            st.subheader("処理結果")

            input_rows = (
                quality["accepted_rows"]
                + quality["rejected_rows"]
                + quality["excluded_duplicate_rows"]
            )

            st.write(f"**入力データ：{input_rows:,}件**")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "✓ 正常",
                f'{quality["accepted_rows"]:,}件',
            )

            col2.metric(
                "⚠ 要確認",
                f'{quality["rejected_rows"]:,}件',
            )

            col3.metric(
                "✕ 除外",
                f'{quality["excluded_duplicate_rows"]:,}件',
            )

            if quality["fatal_files"]:
                st.warning(
                    f'{len(quality["fatal_files"])}ファイルを処理できませんでした。'
                )

            st.subheader("作成したファイル")

            for name in outputs:
                st.markdown(
                    f"**✓ `{name}`**  \n"
                    f"{OUTPUT_DESCRIPTIONS.get(name, '')}"
                )

            if len(outputs) == 1:
                name, data = next(iter(outputs.items()))

                st.download_button(
                    "作成したファイルをダウンロード",
                    data=data,
                    file_name=name,
                    width="stretch",
                )

            else:
                st.download_button(
                    f"{len(outputs)}ファイルをまとめてダウンロード",
                    data=zip_outputs(outputs),
                    file_name="csv_data_bridge_output.zip",
                    mime="application/zip",
                    width="stretch",
                )

        except Exception as exc:
            logger.exception("Conversion failed: %s", exc)

            st.error(
                "変換処理でエラーが発生しました。"
                "サンプルデータまたは変換設定を確認してください。"
            )
