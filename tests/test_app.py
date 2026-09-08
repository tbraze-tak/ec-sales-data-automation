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
