from __future__ import annotations

import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "sample_data" / "input"
PRODUCTS = [(f"P-{i:03d}", f"Synthetic Product {i:02d}", 800 + i * 175) for i in range(1, 25)]


def rows(count: int, prefix: str, seed: int) -> list[dict[str, object]]:
    start = date(2025, 9, 1)
    result = []
    for index in range(count):
        sku, product, price = PRODUCTS[(index * 7 + seed) % len(PRODUCTS)]
        quantity = 1 + (index + seed) % 5
        status = "cancelled" if index % 41 == 0 else "refunded" if index % 97 == 0 else "completed"
        result.append({
            "order_id": f"{prefix}-{index + 1:05d}",
            "order_date": start + timedelta(days=(index * 11 + seed * 3) % 365),
            "status": status,
            "sku": sku,
            "product": product,
            "quantity": quantity,
            "price": price,
            "discount": 200 if index % 9 == 0 else 0,
            "shipping": 450 if index % 4 == 0 else 0,
            "tax": round(quantity * price * 0.1),
        })
    return result


def write_csv(path: Path, fields: list[str], output_rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    north = rows(340, "N", 1)
    sakura = rows(342, "S", 2)
    harbor = rows(342, "H", 3)
    sakura[-1] = dict(sakura[-2])
    harbor[-1]["quantity"] = "not-a-number"

    status_n = {"completed": "paid", "cancelled": "cancelled", "refunded": "refunded"}
    write_csv(OUTPUT / "north_market_2026.csv", ["order_no", "order_date", "status", "sku", "item", "qty", "unit_price", "discount", "shipping", "tax"], [{
        "order_no": r["order_id"], "order_date": r["order_date"].isoformat(), "status": status_n[r["status"]],
        "sku": r["sku"], "item": r["product"], "qty": r["quantity"], "unit_price": r["price"],
        "discount": r["discount"], "shipping": r["shipping"], "tax": r["tax"],
    } for r in north])

    status_s = {"completed": "発送済", "cancelled": "キャンセル", "refunded": "返金"}
    write_csv(OUTPUT / "sakura_mall_2026.csv", ["注文番号", "注文日", "状態", "商品コード", "商品名", "個数", "販売単価", "クーポン", "送料", "消費税"], [{
        "注文番号": r["order_id"], "注文日": r["order_date"].strftime("%Y/%m/%d"), "状態": status_s[r["status"]],
        "商品コード": r["sku"], "商品名": r["product"], "個数": r["quantity"], "販売単価": r["price"],
        "クーポン": r["discount"], "送料": r["shipping"], "消費税": r["tax"],
    } for r in sakura])

    status_h = {"completed": "fulfilled", "cancelled": "void", "refunded": "refunded"}
    write_csv(OUTPUT / "harbor_shop_2026.csv", ["id", "created_at", "state", "product_code", "description", "units", "price_jpy", "discount_jpy", "delivery_jpy", "tax_jpy"], [{
        "id": r["order_id"], "created_at": datetime.combine(r["order_date"], datetime.min.time(), timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "state": status_h[r["status"]], "product_code": r["sku"], "description": r["product"], "units": r["quantity"],
        "price_jpy": r["price"], "discount_jpy": r["discount"], "delivery_jpy": r["shipping"], "tax_jpy": r["tax"],
    } for r in harbor])
    print("Generated 1,024 wholly synthetic rows")


if __name__ == "__main__":
    main()
