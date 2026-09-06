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
    "discount_amount", "shipping_amount", "tax_amount", "gross_sales",
    "net_sales", "currency"
]


@dataclass(frozen=True)
class Rejection:
    source_file: str
    source_row: int | None
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


def _normalize_row(
    source_key: str,
    cfg: dict[str, Any],
    source_file: str,
    source_row: int,
    raw: dict[str, str],
    currency: str,
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
    tax = _decimal(mapped.get("tax_amount"), "tax_amount")

    if status == "cancelled":
        quantity_out, unit_price_out = quantity, unit_price
        gross = net = Decimal("0")
        discount_out = shipping_out = tax_out = Decimal("0")
    else:
        sign = Decimal("-1") if status == "refunded" else Decimal("1")
        quantity_out = -quantity if status == "refunded" else quantity
        unit_price_out = unit_price
        discount_out = discount * sign
        shipping_out = shipping * sign
        tax_out = tax * sign
        gross = Decimal(quantity) * unit_price * sign
        net = gross - discount_out + shipping_out + tax_out

    return {
        "source_channel": cfg["display_name"],
        "source_file": source_file,
        "source_row": source_row,
        "order_id": mapped["order_id"].strip(),
        "order_date": _parse_date(mapped.get("order_date") or "", cfg["date_formats"]),
        "order_status": status,
        "product_id": mapped["product_id"].strip(),
        "product_name": mapped["product_name"].strip(),
        "quantity": quantity_out,
        "unit_price": int(unit_price_out),
        "discount_amount": int(discount_out),
        "shipping_amount": int(shipping_out),
        "tax_amount": int(tax_out),
        "gross_sales": int(gross),
        "net_sales": int(net),
        "currency": currency,
        "_source_key": source_key,
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed_orders = {f'{r["source_channel"]}:{r["order_id"]}' for r in rows if r["order_status"] == "completed"}
    monthly: dict[str, dict[str, int]] = defaultdict(lambda: {"net_sales": 0, "units": 0})
    channels: dict[str, dict[str, int]] = defaultdict(lambda: {"net_sales": 0, "orders": 0, "units": 0})
    products: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"net_sales": 0, "units": 0})
    channel_orders: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        if row["order_status"] == "cancelled":
            continue
        month = row["order_date"][:7]
        monthly[month]["net_sales"] += row["net_sales"]
        monthly[month]["units"] += row["quantity"]
        channel = row["source_channel"]
        channels[channel]["net_sales"] += row["net_sales"]
        channels[channel]["units"] += row["quantity"]
        if row["order_status"] == "completed":
            channel_orders[channel].add(row["order_id"])
        product = (row["product_id"], row["product_name"])
        products[product]["net_sales"] += row["net_sales"]
        products[product]["units"] += row["quantity"]

    for channel, values in channels.items():
        values["orders"] = len(channel_orders[channel])

    total_net = sum(r["net_sales"] for r in rows if r["order_status"] != "cancelled")
    units = sum(r["quantity"] for r in rows if r["order_status"] != "cancelled")
    order_count = len(completed_orders)
    months = sorted(monthly)
    monthly_rows = []
    for index, month in enumerate(months):
        current = monthly[month]["net_sales"]
        previous = monthly[months[index - 1]]["net_sales"] if index else None
        mom = None if previous in (None, 0) else (current - previous) / previous
        monthly_rows.append({"month": month, **monthly[month], "mom_change": mom})

    return {
        "kpis": {
            "net_sales": total_net,
            "completed_orders": order_count,
            "units": units,
            "average_order_value": round(total_net / order_count) if order_count else None,
            "latest_mom_change": monthly_rows[-1]["mom_change"] if monthly_rows else None,
        },
        "monthly": monthly_rows,
        "channels": [{"channel": key, **value} for key, value in sorted(channels.items())],
        "products": [
            {"product_id": key[0], "product_name": key[1], **value}
            for key, value in sorted(products.items(), key=lambda item: (-item[1]["net_sales"], item[0][0]))
        ],
    }


def run_pipeline(input_dir: Path, output_dir: Path, contract_path: Path) -> dict[str, Any]:
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
            source_key, cfg = _match_source(path.name, contract["sources"])
            with path.open("r", encoding=cfg["encoding"], newline="") as handle:
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
                            source_key, cfg, path.name, row_number, raw, contract["currency"]
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
                        rejections.append(Rejection(path.name, row_number, "invalid_row", str(exc)))
                file_info.append({
                    "name": path.name,
                    "source": cfg["display_name"],
                    "rows": file_count,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                })
        except (OSError, UnicodeError, csv.Error, PipelineError) as exc:
            fatal_files.append({"name": path.name, "error": str(exc)})

    if fatal_files:
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
