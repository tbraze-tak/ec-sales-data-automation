from __future__ import annotations

import csv
import io
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

from .pipeline import PipelineError, detect_source, load_contract, run_pipeline


BRIDGE_COLUMNS = [
    "store", "order_id", "order_date", "year_month", "status", "sku", "product_name",
    "quantity", "unit_price", "gross_item_amount", "discount_amount", "shipping_amount",
    "tax_category", "tax_rate", "tax_amount", "total_amount", "source_file",
]


def _decode_csv(data: bytes, filename: str) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "cp932"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise PipelineError(f"{filename}: UTF-8またはCP932のCSVとして読み込めません")


def identify_csv(data: bytes, filename: str, contract_path: Path) -> dict[str, object]:
    contract = load_contract(contract_path)
    text, encoding = _decode_csv(data, filename)
    reader = csv.DictReader(io.StringIO(text))
    source_key, cfg = detect_source(reader.fieldnames or [], contract["sources"])
    rows = sum(1 for _ in reader)
    return {"source_key": source_key, "source_name": cfg["display_name"], "rows": rows, "encoding": encoding}


def canonical_rows(model: dict) -> list[dict[str, object]]:
    rows = []
    for row in model["clean_data"]:
        rows.append({
            "store": row["source_channel"],
            "order_id": row["order_id"],
            "order_date": row["order_date"],
            "year_month": row["order_date"][:7],
            "status": row["order_status"],
            "sku": row["product_id"],
            "product_name": row["product_name"],
            "quantity": row["quantity"],
            "unit_price": row["unit_price"],
            "gross_item_amount": row["gross_item_amount"],
            "discount_amount": row["discount_amount"],
            "shipping_amount": row["shipping_amount"],
            "tax_category": row["tax_category"],
            "tax_rate": row["tax_rate"],
            "tax_amount": row["tax_amount"],
            "total_amount": row["total_amount"],
            "source_file": row["source_file"],
        })
    return rows


def clean_csv_bytes(model: dict) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=BRIDGE_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(canonical_rows(model))
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def accounting_demo_bytes(model: dict) -> bytes:
    columns = [
        "transaction_date", "document_no", "debit_account", "debit_amount",
        "credit_account", "credit_amount", "tax_category", "description",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in canonical_rows(model):
        if row["status"] == "cancelled":
            continue
        amount = -row["total_amount"] if row["status"] == "refunded" else row["total_amount"]
        writer.writerow({
            "transaction_date": row["order_date"],
            "document_no": row["order_id"],
            "debit_account": "Accounts Receivable",
            "debit_amount": amount,
            "credit_account": "Sales",
            "credit_amount": amount,
            "tax_category": f'DEMO_{str(row["tax_category"]).upper()}_{int(float(row["tax_rate"])*100)}PCT',
            "description": f'{row["store"]} / {row["product_name"]}',
        })
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def process_uploads(files: Iterable[tuple[str, bytes]], contract_path: Path) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        input_dir = root / "input"
        input_dir.mkdir()
        for index, (name, data) in enumerate(files):
            safe_name = Path(name).name or f"upload_{index}.csv"
            text, _ = _decode_csv(data, safe_name)
            (input_dir / f"{index:03d}_{safe_name}").write_text(text, encoding="utf-8-sig", newline="")
        return run_pipeline(input_dir, root / "output", contract_path, allow_partial=True)


def zip_outputs(outputs: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in outputs.items():
            archive.writestr(name, data)
    return buffer.getvalue()
