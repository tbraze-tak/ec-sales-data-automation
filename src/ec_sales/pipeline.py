from __future__ import annotations

import csv
import fnmatch
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SENSITIVE_WORDS = {
    "customer", "buyer", "address", "email", "phone", "mobile", "card", "token",
}
SENSITIVE_JAPANESE = {"氏名", "住所", "メール", "電話", "購入者", "顧客"}

CANONICAL_COLUMNS = [
    "source_channel", "source_file", "source_row", "order_id", "order_date",
    "order_status", "product_id", "product_name", "quantity", "unit_price",
    "gross_item_amount", "discount_amount", "shipping_amount", "tax_category",
    "tax_rate", "tax_amount", "total_amount", "currency"
]


@dataclass(frozen=True)
class Rejection:
    source_file: str
    source_row: int | None
    order_id: str | None
    reason: str
    detail: str


class PipelineError(RuntimeError):
    pass


def load_contract(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _match_source(filename: str, sources: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    matches = [(key, cfg) for key, cfg in sources.items() if fnmatch.fnmatch(filename, cfg["file_pattern"])]
    if len(matches) != 1:
        raise PipelineError(f"{filename}: expected exactly one source adapter, found {len(matches)}")
    return matches[0]


def detect_source(columns: list[str], sources: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Identify one configured adapter from its required column set."""
    available = set(columns)
    matches = [
        (key, cfg) for key, cfg in sources.items()
        if set(cfg["required"]).issubset(available)
    ]
    if len(matches) != 1:
        raise PipelineError(f"expected exactly one source adapter from headers, found {len(matches)}")
    return matches[0]


def _has_sensitive_column(columns: list[str]) -> list[str]:
    sensitive = []
    for column in columns:
        words = set(filter(None, re.split(r"[^a-z0-9]+", column.casefold())))
        if words & SENSITIVE_WORDS or any(token in column for token in SENSITIVE_JAPANESE):
            sensitive.append(column)
    return sensitive


def _parse_date(value: str, formats: list[str]) -> str:
    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"invalid date: {value!r}")


def _decimal(value: str | None, field: str) -> Decimal:
    text = (value or "").strip().replace(",", "")
    if text == "":
        return Decimal("0")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid {field}: {value!r}") from exc
    if number != number.to_integral_value():
        raise ValueError(f"fractional JPY not allowed for {field}: {value!r}")
    if number < 0:
        raise ValueError(f"negative source value not allowed for {field}: {value!r}")
    return number


def _integer(value: str | None, field: str) -> int:
    try:
        result = int((value or "").strip())
    except ValueError as exc:
        raise ValueError(f"invalid {field}: {value!r}") from exc
    if result <= 0:
        raise ValueError(f"{field} must be positive: {value!r}")
    return result


def _tax_definition(product_id: str, product_tax_master: dict[str, Any]) -> tuple[str, Decimal]:
    """Read the synthetic demo tax definition from the explicit product master."""
    definition = product_tax_master.get(product_id)
    if not isinstance(definition, dict):
        raise ValueError(f"missing tax definition for product_id: {product_id!r}")
    category = str(definition.get("category") or "").strip()
    try:
        rate = Decimal(str(definition.get("rate")))
    except InvalidOperation as exc:
        raise ValueError(f"invalid tax rate for product_id: {product_id!r}") from exc
    if not category or rate < 0 or rate > 1:
        raise ValueError(f"invalid tax definition for product_id: {product_id!r}")
    return category, rate


def _normalize_row(
    source_key: str,
    cfg: dict[str, Any],
    source_file: str,
    source_row: int,
    raw: dict[str, str],
    currency: str,
    product_tax_master: dict[str, Any],
) -> dict[str, Any]:
    mapped = {target: raw.get(source) for source, target in cfg["columns"].items()}
    for field in ("order_id", "product_id", "product_name"):
        if not (mapped.get(field) or "").strip():
            raise ValueError(f"missing {field}")

    source_status = (mapped.get("order_status") or "").strip()
    try:
        status = cfg["status_map"][source_status]
    except KeyError as exc:
        raise ValueError(f"unknown status: {source_status!r}") from exc

    quantity = _integer(mapped.get("quantity"), "quantity")
    unit_price = _decimal(mapped.get("unit_price"), "unit_price")
    discount = _decimal(mapped.get("discount_amount"), "discount_amount")
    shipping = _decimal(mapped.get("shipping_amount"), "shipping_amount")
    source_tax = _decimal(mapped.get("tax_amount"), "tax_amount")
    product_id = mapped["product_id"].strip()
    tax_category, tax_rate = _tax_definition(product_id, product_tax_master)
    gross = Decimal(quantity) * unit_price

    # Canonical data preserves source meaning. Cancelled/refunded rows remain positive.
    # The synthetic input generator calculates tax using its explicit product tax master.
    tax = source_tax
    total = gross - discount + shipping + tax

    return {
        "source_channel": cfg["display_name"],
        "source_file": source_file,
        "source_row": source_row,
        "order_id": mapped["order_id"].strip(),
        "order_date": _parse_date(mapped.get("order_date") or "", cfg["date_formats"]),
        "order_status": status,
        "product_id": product_id,
        "product_name": mapped["product_name"].strip(),
        "quantity": quantity,
        "unit_price": int(unit_price),
        "gross_item_amount": int(gross),
        "discount_amount": int(discount),
        "shipping_amount": int(shipping),
        "tax_category": tax_category,
        "tax_rate": float(tax_rate),
        "tax_amount": int(tax),
        "total_amount": int(total),
        "currency": currency,
        "_source_key": source_key,
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [r for r in rows if r["order_status"] == "completed"]
    refunded = [r for r in rows if r["order_status"] == "refunded"]
    completed_orders = {f'{r["source_channel"]}:{r["order_id"]}' for r in completed}

    def blank():
        return {"product_sales": 0, "refund_product_amount": 0, "net_product_sales": 0,
                "sales_quantity": 0, "refund_quantity": 0, "net_quantity": 0,
                "orders": 0, "total_billed": 0, "discount": 0, "shipping": 0, "tax": 0}

    monthly, stores, products, taxes = {}, {}, {}, {}
    order_sets = {
        "monthly": defaultdict(set),
        "stores": defaultdict(set),
        "products": defaultdict(set),
        "taxes": defaultdict(set),
    }
    for r in rows:
        if r["order_status"] == "cancelled":
            continue
        keys = [
            ("monthly", monthly, r["order_date"][:7]),
            ("stores", stores, r["source_channel"]),
            ("products", products, (r["product_id"], r["product_name"])),
            ("taxes", taxes, (r["tax_category"], r["tax_rate"])),
        ]
        for dimension, mapping, key in keys:
            if key not in mapping: mapping[key] = blank()
            a=mapping[key]
            if r["order_status"] == "completed":
                a["product_sales"] += r["gross_item_amount"]
                a["sales_quantity"] += r["quantity"]
                a["total_billed"] += r["total_amount"]
                a["discount"] += r["discount_amount"]
                a["shipping"] += r["shipping_amount"]
                a["tax"] += r["tax_amount"]
            elif r["order_status"] == "refunded":
                a["refund_product_amount"] += r["gross_item_amount"]
                a["refund_quantity"] += r["quantity"]
                a["total_billed"] -= r["total_amount"]
                a["discount"] -= r["discount_amount"]
                a["shipping"] -= r["shipping_amount"]
                a["tax"] -= r["tax_amount"]
            a["net_product_sales"] = a["product_sales"] - a["refund_product_amount"]
            a["net_quantity"] = a["sales_quantity"] - a["refund_quantity"]
            if r["order_status"] == "completed":
                order_sets[dimension][key].add((r["source_channel"], r["order_id"]))

    k=blank()
    k.update({
        "product_sales": sum(r["gross_item_amount"] for r in completed),
        "refund_product_amount": sum(r["gross_item_amount"] for r in refunded),
        "sales_quantity": sum(r["quantity"] for r in completed),
        "refund_quantity": sum(r["quantity"] for r in refunded),
        "completed_orders": len(completed_orders),
        "total_billed": sum(r["total_amount"] for r in completed)-sum(r["total_amount"] for r in refunded),
        "discount": sum(r["discount_amount"] for r in completed)-sum(r["discount_amount"] for r in refunded),
        "shipping": sum(r["shipping_amount"] for r in completed)-sum(r["shipping_amount"] for r in refunded),
        "tax": sum(r["tax_amount"] for r in completed)-sum(r["tax_amount"] for r in refunded),
    })
    k["net_product_sales"] = k["product_sales"]-k["refund_product_amount"]
    k["net_quantity"] = k["sales_quantity"]-k["refund_quantity"]
    for dimension, mapping in (
        ("monthly", monthly),
        ("stores", stores),
        ("products", products),
        ("taxes", taxes),
    ):
        for key, values in mapping.items():
            values["orders"] = len(order_sets[dimension][key])
    return {
        "kpis": k,
        "monthly": [{"month": key, **monthly[key]} for key in sorted(monthly)],
        "stores": [{"store": key, **stores[key]} for key in sorted(stores)],
        "products": [{"product_id": key[0], "product_name": key[1], **value} for key,value in sorted(products.items())],
        "taxes": [{"tax_category": key[0], "tax_rate": key[1], **value} for key,value in sorted(taxes.items(), key=lambda x:x[0][1])],
    }


def run_pipeline(
    input_dir: Path,
    output_dir: Path,
    contract_path: Path,
    *,
    allow_partial: bool = False,
) -> dict[str, Any]:
    contract = load_contract(contract_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise PipelineError(f"no CSV files found in {input_dir}")

    accepted: list[dict[str, Any]] = []
    rejections: list[Rejection] = []
    fatal_files: list[dict[str, str]] = []
    input_rows = 0
    duplicates = 0
    seen: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    file_info = []

    for path in files:
        try:
            try:
                source_key, cfg = _match_source(path.name, contract["sources"])
                encoding = cfg["encoding"]
            except PipelineError:
                encoding = "utf-8-sig"
                with path.open("r", encoding=encoding, newline="") as probe:
                    columns = csv.DictReader(probe).fieldnames or []
                source_key, cfg = detect_source(columns, contract["sources"])
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle)
                columns = reader.fieldnames or []
                missing = sorted(set(cfg["required"]) - set(columns))
                sensitive = _has_sensitive_column(columns)
                if missing:
                    raise PipelineError(f"missing required columns: {missing}")
                if sensitive:
                    raise PipelineError(f"sensitive columns are not allowed: {sensitive}")
                file_count = 0
                for row_number, raw in enumerate(reader, start=2):
                    input_rows += 1
                    file_count += 1
                    try:
                        normalized = _normalize_row(
                            source_key,
                            cfg,
                            path.name,
                            row_number,
                            raw,
                            contract["currency"],
                            contract.get("product_tax_master", {}),
                        )
                        identity = (
                            source_key, normalized["order_id"], normalized["product_id"], normalized["order_status"]
                        )
                        comparable = {k: v for k, v in normalized.items() if k not in {"source_file", "source_row"}}
                        if identity in seen:
                            previous = {k: v for k, v in seen[identity].items() if k not in {"source_file", "source_row"}}
                            if comparable == previous:
                                duplicates += 1
                                continue
                            raise ValueError(f"duplicate_conflict for identity {identity}")
                        seen[identity] = normalized
                        accepted.append(normalized)
                    except ValueError as exc:
                        order_column = next(
                            (source for source, target in cfg["columns"].items() if target == "order_id"),
                            None,
                        )
                        rejections.append(Rejection(
                            path.name,
                            row_number,
                            (raw.get(order_column) or "").strip() if order_column else None,
                            "invalid_row",
                            str(exc),
                        ))
                file_info.append({
                    "name": path.name,
                    "source": cfg["display_name"],
                    "rows": file_count,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                })
        except (OSError, UnicodeError, csv.Error, PipelineError) as exc:
            fatal_files.append({"name": path.name, "error": str(exc)})

    if fatal_files and not allow_partial:
        report = {"fatal_files": fatal_files, "input_rows": input_rows}
        (output_dir / "quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        raise PipelineError(f"fatal input errors: {len(fatal_files)} file(s)")

    quality = {
        "contract_version": contract["contract_version"],
        "files": file_info,
        "input_rows": input_rows,
        "accepted_rows": len(accepted),
        "excluded_duplicate_rows": duplicates,
        "rejected_rows": len(rejections),
        "reconciliation_ok": input_rows == len(accepted) + duplicates + len(rejections),
        "rejections": [asdict(item) for item in rejections],
        "fatal_files": [],
    }
    model = _aggregate(accepted)
    model["quality"] = quality
    model["clean_data"] = [{key: row[key] for key in CANONICAL_COLUMNS} for row in accepted]

    with (output_dir / "clean_data.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANONICAL_COLUMNS)
        writer.writeheader()
        writer.writerows({key: row[key] for key in CANONICAL_COLUMNS} for row in accepted)
    (output_dir / "quality_report.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "report_model.json").write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return model
