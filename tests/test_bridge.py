import csv
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from ec_sales.bridge import accounting_demo_bytes, clean_csv_bytes, identify_csv, process_uploads, zip_outputs
from ec_sales.output_adapters import build_excel_report
from ec_sales.pipeline import PipelineError, run_pipeline


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "source_contracts.json"


class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as directory:
            cls.model = run_pipeline(ROOT / "sample_data" / "input", Path(directory), CONTRACT)

    def test_large_synthetic_sample_and_three_sources(self):
        quality = self.model["quality"]
        self.assertEqual(quality["input_rows"], 1024)
        self.assertEqual(quality["accepted_rows"], 1022)
        self.assertEqual(quality["excluded_duplicate_rows"], 1)
        self.assertEqual(quality["rejected_rows"], 1)
        self.assertEqual(len(quality["files"]), 3)
        self.assertTrue(quality["reconciliation_ok"])
        totals = [
            self.model["kpis"]["net_sales"],
            sum(row["net_sales"] for row in self.model["monthly"]),
            sum(row["net_sales"] for row in self.model["channels"]),
            sum(row["net_sales"] for row in self.model["products"]),
            sum(row["net_sales"] for row in self.model["clean_data"]),
        ]
        self.assertEqual(len(set(totals)), 1)
        completed_orders = {
            (row["source_channel"], row["order_id"])
            for row in self.model["clean_data"] if row["order_status"] == "completed"
        }
        self.assertEqual(self.model["kpis"]["completed_orders"], len(completed_orders))

    def test_header_detection_does_not_require_filename(self):
        data = (ROOT / "sample_data" / "input" / "north_market_2026.csv").read_bytes()
        result = identify_csv(data, "customer_export.csv", CONTRACT)
        self.assertEqual(result["source_key"], "north_market")
        self.assertEqual(result["rows"], 340)

    def test_uploaded_cp932_csv_is_normalized(self):
        text = "注文番号,注文日,状態,商品コード,商品名,個数,販売単価\nS-1,2026/08/01,発送済,P-1,合成商品,1,1000\n"
        result = identify_csv(text.encode("cp932"), "export.csv", CONTRACT)
        self.assertEqual(result["source_key"], "sakura_mall")
        model = process_uploads([("export.csv", text.encode("cp932"))], CONTRACT)
        self.assertEqual(model["quality"]["accepted_rows"], 1)

    def test_unknown_schema_is_reported(self):
        with self.assertRaises(PipelineError):
            identify_csv(b"unknown,value\n1,2\n", "unknown.csv", CONTRACT)

    def test_clean_csv_and_accounting_demo(self):
        clean = list(csv.DictReader(io.StringIO(clean_csv_bytes(self.model).decode("utf-8-sig"))))
        accounting = list(csv.DictReader(io.StringIO(accounting_demo_bytes(self.model).decode("utf-8-sig"))))
        self.assertEqual(len(clean), self.model["quality"]["accepted_rows"])
        self.assertEqual(sum(int(row["net_sales"]) for row in clean), self.model["kpis"]["net_sales"])
        self.assertTrue(accounting)
        self.assertEqual({row["tax_category"] for row in accounting}, {"DEMO_STANDARD"})
        self.assertEqual(sum(int(row["debit_amount"]) for row in accounting), sum(int(row["credit_amount"]) for row in accounting))

    def test_excel_aggregates_are_formula_linked(self):
        workbook = build_excel_report(self.model)
        with zipfile.ZipFile(io.BytesIO(workbook)) as archive:
            sheets = b"".join(archive.read(name) for name in archive.namelist() if name.startswith("xl/worksheets/sheet"))
        self.assertIn(b"SUMIFS(Clean_Data!", sheets)
        self.assertIn(b"SUM(Monthly!", sheets)
        self.assertIn(b"SUM(Channel!", sheets)
        self.assertIn(b"SUM(Product!", sheets)
        self.assertIn(b"SUM(Clean_Data!", sheets)

    def test_multiple_outputs_are_zipped(self):
        payload = zip_outputs({"clean_sales_data.csv": b"a,b\n1,2\n", "accounting_import_demo.csv": b"x,y\n3,4\n"})
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            self.assertEqual(set(archive.namelist()), {"clean_sales_data.csv", "accounting_import_demo.csv"})


if __name__ == "__main__":
    unittest.main()
