import json
import csv
import tempfile
import unittest
from pathlib import Path

from ec_sales.pipeline import PipelineError, run_pipeline


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def write_csv(self, directory, filename, headers, rows):
        path = Path(directory) / filename
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def test_sample_pipeline_reconciles_and_aggregates(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            model = run_pipeline(
                ROOT / "sample_data" / "small_input",
                output,
                ROOT / "config" / "source_contracts.json",
            )

            self.assertEqual(model["quality"]["input_rows"], 12)
            self.assertEqual(model["quality"]["accepted_rows"], 10)
            self.assertEqual(model["quality"]["excluded_duplicate_rows"], 1)
            self.assertEqual(model["quality"]["rejected_rows"], 1)
            self.assertTrue(model["quality"]["reconciliation_ok"])
            self.assertEqual(model["kpis"]["sales_quantity"], 17)
            self.assertEqual(model["kpis"]["refund_quantity"], 1)
            self.assertEqual(model["kpis"]["net_quantity"], 16)
            self.assertEqual(model["kpis"]["total_billed"], 36590)
            self.assertTrue(all(r["quantity"] > 0 for r in model["clean_data"] if r["order_status"] == "refunded"))

            quality = json.loads((output / "quality_report.json").read_text(encoding="utf-8"))
            self.assertTrue(quality["reconciliation_ok"])
            self.assertIn("invalid quantity", quality["rejections"][0]["detail"])

    def test_outputs_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first"
            second = root / "second"
            run_pipeline(ROOT / "sample_data" / "small_input", first, ROOT / "config" / "source_contracts.json")
            run_pipeline(ROOT / "sample_data" / "small_input", second, ROOT / "config" / "source_contracts.json")

            for filename in ("clean_data.csv", "quality_report.json", "report_model.json"):
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())

    def test_missing_required_column_is_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root, "north_market_bad.csv", ["order_no", "order_date"], [["N-1", "2026-08-01"]])
            with self.assertRaisesRegex(PipelineError, "fatal input errors"):
                run_pipeline(root, root / "out", ROOT / "config" / "source_contracts.json")
            report = json.loads((root / "out" / "quality_report.json").read_text(encoding="utf-8"))
            self.assertIn("missing required columns", report["fatal_files"][0]["error"])

    def test_sensitive_column_is_fatal_but_product_name_is_not(self):
        headers = ["order_no", "order_date", "status", "sku", "item", "qty", "unit_price", "customer_email"]
        row = ["N-1", "2026-08-01", "paid", "P-1", "Sample", "1", "1000", "person@example.test"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root, "north_market_sensitive.csv", headers, [row])
            with self.assertRaises(PipelineError):
                run_pipeline(root, root / "out", ROOT / "config" / "source_contracts.json")
            report = json.loads((root / "out" / "quality_report.json").read_text(encoding="utf-8"))
            self.assertIn("customer_email", report["fatal_files"][0]["error"])

    def test_unknown_source_file_is_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root, "unknown.csv", ["id"], [["1"]])
            with self.assertRaises(PipelineError):
                run_pipeline(root, root / "out", ROOT / "config" / "source_contracts.json")

    def test_invalid_date_and_fractional_yen_are_rejected(self):
        headers = ["order_no", "order_date", "status", "sku", "item", "qty", "unit_price"]
        rows = [
            ["N-1", "08-01-2026", "paid", "P-1", "Sample", "1", "1000"],
            ["N-2", "2026-08-01", "paid", "P-2", "Sample 2", "1", "1000.5"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root, "north_market_invalid.csv", headers, rows)
            model = run_pipeline(root, root / "out", ROOT / "config" / "source_contracts.json")
            self.assertEqual(model["quality"]["rejected_rows"], 2)
            self.assertEqual(model["quality"]["accepted_rows"], 0)
            self.assertTrue(model["quality"]["reconciliation_ok"])

    def test_conflicting_duplicate_is_rejected(self):
        headers = ["order_no", "order_date", "status", "sku", "item", "qty", "unit_price"]
        rows = [
            ["N-1", "2026-08-01", "paid", "P-001", "Sample", "1", "1000"],
            ["N-1", "2026-08-01", "paid", "P-001", "Sample", "2", "1000"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root, "north_market_conflict.csv", headers, rows)
            model = run_pipeline(root, root / "out", ROOT / "config" / "source_contracts.json")
            self.assertEqual(model["quality"]["accepted_rows"], 1)
            self.assertEqual(model["quality"]["rejected_rows"], 1)
            self.assertIn("duplicate_conflict", model["quality"]["rejections"][0]["detail"])

    def test_empty_input_directory_is_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(PipelineError, "no CSV files"):
                run_pipeline(root, root / "out", ROOT / "config" / "source_contracts.json")

    def test_product_without_tax_master_entry_is_rejected(self):
        headers = ["order_no", "order_date", "status", "sku", "item", "qty", "unit_price"]
        row = ["N-1", "2026-08-01", "paid", "P-999", "Unknown synthetic product", "1", "1000"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_csv(root, "north_market_unknown_product.csv", headers, [row])
            model = run_pipeline(root, root / "out", ROOT / "config" / "source_contracts.json")
            self.assertEqual(model["quality"]["accepted_rows"], 0)
            self.assertEqual(model["quality"]["rejected_rows"], 1)
            self.assertIn("missing tax definition", model["quality"]["rejections"][0]["detail"])


if __name__ == "__main__":
    unittest.main()
