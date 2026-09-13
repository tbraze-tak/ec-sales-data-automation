import re
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_sample_demo_flow_completes_without_streamlit_errors():
    app = AppTest.from_file(ROOT / "app.py").run()
    assert not app.exception
    assert [item.value for item in app.title] == ["複数店舗の売上データを一括集計"]
    assert len(app.get("download_button")) == 3

    app.button[0].click().run()
    assert not app.exception
    assert [item.value for item in app.title] == ["3店舗の売上データをまとめてみましょう"]

    app.button[1].click().run()
    assert not app.exception
    assert any("3店舗・1,024件" in item.value for item in app.success)

    app.button[2].click().run()
    assert not app.exception
    assert any("変換が完了しました" in item.value for item in app.success)
    assert len(app.get("download_button")) == 1


def _complete_three_output_demo(language: str):
    app = AppTest.from_file(ROOT / "app.py").run()
    app.radio[0].set_value(language).run()
    app.button[0].click().run()
    app.button[1].click().run()
    app.checkbox[2].set_value(True).run()
    app.button[2].click().run()
    assert not app.exception
    return app


def test_english_demo_flow_matches_japanese_results_and_outputs():
    japanese = _complete_three_output_demo("日本語")
    english = _complete_three_output_demo("English")

    assert [item.value for item in english.title] == [
        "Combine Sales Data from Three Stores"
    ]
    assert any("Loaded 1,024 sales rows from 3 stores" in item.value for item in english.success)
    assert any("Processing complete" in item.value for item in english.success)
    assert [item.value for item in english.metric] == ["1,022", "1", "1"]
    english_counts = [int(re.sub(r"\D", "", item.value)) for item in english.metric]
    japanese_counts = [int(re.sub(r"\D", "", item.value)) for item in japanese.metric]
    assert english_counts == japanese_counts == [1022, 1, 1]

    expected_files = {
        "clean_sales_data.csv",
        "sales_report.xlsx",
        "accounting_import_demo.csv",
    }
    for app in (japanese, english):
        generated_files = {
            match.group(1)
            for item in app.markdown
            if (match := re.search(r"`([^`]+)`", item.value))
        }
        assert generated_files == expected_files
        assert len(app.get("download_button")) == 1

    assert any("DEMO output only" in item.value for item in english.caption)
    assert any("DEMO only" in item.value for item in english.markdown)
