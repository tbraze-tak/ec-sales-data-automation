from __future__ import annotations

import io
from datetime import datetime

import xlsxwriter

from ec_sales.bridge import BRIDGE_COLUMNS, canonical_rows


def _excel_text(value: object) -> str:
    return str(value).replace('"', '""')


def build_excel_report(model: dict) -> bytes:
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
    workbook.set_properties(
        {
            "title": "CSV Data Bridge 売上レポート",
            "comments": "完全合成データによるデモレポート",
        }
    )

    title = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#17324D"})
    header = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#17324D",
            "font_color": "#FFFFFF",
            "align": "center",
            "valign": "vcenter",
        }
    )
    money = workbook.add_format({"num_format": '#,##0"円";[Red]-#,##0"円"', "align": "right"})
    integer = workbook.add_format({"num_format": "#,##0", "align": "right"})
    percent = workbook.add_format({"num_format": "0%", "align": "right"})
    date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})
    note = workbook.add_format({"font_color": "#4B5563", "italic": True})

    names = (
        "Dashboard",
        "Monthly",
        "Store",
        "Product",
        "Tax",
        "Clean_Data",
        "Data_Quality",
        "README",
    )
    sheets = {name: workbook.add_worksheet(name) for name in names}
    for sheet in sheets.values():
        sheet.hide_gridlines(2)

    rows = canonical_rows(model)
    clean = sheets["Clean_Data"]
    clean.write("A1", "Canonical Clean Data", title)
    clean.write_row(3, 0, BRIDGE_COLUMNS, header)
    for row_index, row in enumerate(rows, 4):
        for column_index, column in enumerate(BRIDGE_COLUMNS):
            value = row[column]
            if column == "order_date":
                clean.write_datetime(
                    row_index,
                    column_index,
                    datetime.fromisoformat(str(value)),
                    date_format,
                )
            elif column in (
                "quantity",
                "unit_price",
                "gross_item_amount",
                "discount_amount",
                "shipping_amount",
                "tax_amount",
                "total_amount",
            ):
                clean.write_number(
                    row_index,
                    column_index,
                    value,
                    integer if column == "quantity" else money,
                )
            elif column == "tax_rate":
                clean.write_number(row_index, column_index, float(value), percent)
            else:
                clean.write(row_index, column_index, value)
    if rows:
        clean.add_table(
            3,
            0,
            3 + len(rows),
            len(BRIDGE_COLUMNS) - 1,
            {
                "style": "Table Style Medium 2",
                "columns": [{"header": column} for column in BRIDGE_COLUMNS],
            },
        )
    clean.freeze_panes(4, 2)
    clean.set_column("A:A", 16)
    clean.set_column("B:B", 14)
    clean.set_column("C:D", 12)
    clean.set_column("E:F", 11)
    clean.set_column("G:G", 23)
    clean.set_column("H:P", 14)
    clean.set_column("Q:Q", 27)

    clean_first_row = 5
    clean_last_row = 4 + len(rows)
    source_columns = {
        "store": "A",
        "month": "D",
        "status": "E",
        "product": "F",
        "quantity": "H",
        "gross": "J",
        "discount": "K",
        "shipping": "L",
        "tax_category": "M",
        "tax": "O",
        "total": "P",
    }

    def sumifs(value_column: str, status: str, criteria_column: str, criterion: object) -> str:
        criterion_text = _excel_text(criterion)
        return (
            f'=SUMIFS(Clean_Data!${value_column}${clean_first_row}:${value_column}${clean_last_row},'
            f'Clean_Data!$E${clean_first_row}:$E${clean_last_row},"{status}",'
            f'Clean_Data!${criteria_column}${clean_first_row}:${criteria_column}${clean_last_row},'
            f'"{criterion_text}")'
        )

    aggregate_headers = [
        "区分",
        "商品売上",
        "返品商品金額",
        "純商品売上",
        "販売数量",
        "返品数量",
        "純販売数量",
        "注文数",
        "合計請求額",
        "値引額",
        "送料",
        "消費税額",
    ]

    def net_formula(value_column: str, criteria_column: str, criterion: object) -> str:
        completed = sumifs(value_column, "completed", criteria_column, criterion)
        refunded = sumifs(value_column, "refunded", criteria_column, criterion)
        return f"{completed}-{refunded[1:]}"

    def aggregate_sheet(
        name: str,
        items: list[dict],
        label_key: str,
        criteria_key: str,
        criteria_column: str,
    ) -> None:
        sheet = sheets[name]
        sheet.write("A1", f"{name} 集計", title)
        sheet.write("A2", "集計値はClean_Dataを参照する数式で算出しています。", note)
        sheet.write_row(3, 0, aggregate_headers, header)
        for row_index, item in enumerate(items, 4):
            criterion = item[criteria_key]
            sheet.write(row_index, 0, item[label_key])
            excel_row = row_index + 1
            formulas = {
                1: sumifs(source_columns["gross"], "completed", criteria_column, criterion),
                2: sumifs(source_columns["gross"], "refunded", criteria_column, criterion),
                3: f"=B{excel_row}-C{excel_row}",
                4: sumifs(source_columns["quantity"], "completed", criteria_column, criterion),
                5: sumifs(source_columns["quantity"], "refunded", criteria_column, criterion),
                6: f"=E{excel_row}-F{excel_row}",
                8: net_formula(source_columns["total"], criteria_column, criterion),
                9: net_formula(source_columns["discount"], criteria_column, criterion),
                10: net_formula(source_columns["shipping"], criteria_column, criterion),
                11: net_formula(source_columns["tax"], criteria_column, criterion),
            }
            cached_values = {
                1: item["product_sales"],
                2: item["refund_product_amount"],
                3: item["net_product_sales"],
                4: item["sales_quantity"],
                5: item["refund_quantity"],
                6: item["net_quantity"],
                8: item["total_billed"],
                9: item["discount"],
                10: item["shipping"],
                11: item["tax"],
            }
            for column_index, formula in formulas.items():
                cell_format = integer if column_index in (4, 5, 6) else money
                sheet.write_formula(
                    row_index,
                    column_index,
                    formula,
                    cell_format,
                    cached_values[column_index],
                )
            sheet.write_number(row_index, 7, item["orders"], integer)
        sheet.freeze_panes(4, 1)
        sheet.set_column("A:A", 28)
        sheet.set_column("B:L", 15)

    aggregate_sheet("Monthly", model["monthly"], "month", "month", source_columns["month"])
    aggregate_sheet("Store", model["stores"], "store", "store", source_columns["store"])
    products = [
        {"product": f'{item["product_id"]} {item["product_name"]}', **item}
        for item in model["products"]
    ]
    aggregate_sheet("Product", products, "product", "product_id", source_columns["product"])

    tax_sheet = sheets["Tax"]
    tax_sheet.write("A1", "税区分別集計", title)
    tax_sheet.write(
        "A2",
        "通常データは10%・8%。1%は2027年4月以降の制度変更を想定した別テストケースです。",
        note,
    )
    tax_sheet.write_row(3, 0, ["税区分", "税率", *aggregate_headers[1:]], header)
    for row_index, item in enumerate(model["taxes"], 4):
        tax_sheet.write(row_index, 0, item["tax_category"])
        tax_sheet.write_number(row_index, 1, item["tax_rate"], percent)
        criterion = item["tax_category"]
        excel_row = row_index + 1
        values = [
            item["product_sales"],
            item["refund_product_amount"],
            item["net_product_sales"],
            item["sales_quantity"],
            item["refund_quantity"],
            item["net_quantity"],
            item["orders"],
            item["total_billed"],
            item["discount"],
            item["shipping"],
            item["tax"],
        ]
        formulas = [
            sumifs(source_columns["gross"], "completed", source_columns["tax_category"], criterion),
            sumifs(source_columns["gross"], "refunded", source_columns["tax_category"], criterion),
            f"=C{excel_row}-D{excel_row}",
            sumifs(source_columns["quantity"], "completed", source_columns["tax_category"], criterion),
            sumifs(source_columns["quantity"], "refunded", source_columns["tax_category"], criterion),
            f"=F{excel_row}-G{excel_row}",
            None,
            net_formula(source_columns["total"], source_columns["tax_category"], criterion),
            net_formula(source_columns["discount"], source_columns["tax_category"], criterion),
            net_formula(source_columns["shipping"], source_columns["tax_category"], criterion),
            net_formula(source_columns["tax"], source_columns["tax_category"], criterion),
        ]
        for offset, (formula, value) in enumerate(zip(formulas, values), 2):
            cell_format = integer if offset in (5, 6, 7, 8) else money
            if formula is None:
                tax_sheet.write_number(row_index, offset, value, cell_format)
            else:
                tax_sheet.write_formula(row_index, offset, formula, cell_format, value)
    tax_sheet.set_column("A:A", 15)
    tax_sheet.set_column("B:B", 10)
    tax_sheet.set_column("C:M", 15)

    dashboard = sheets["Dashboard"]
    dashboard.write("A1", "CSV Data Bridge 売上ダッシュボード", title)
    dashboard.write("A2", "3店舗の合成売上データを統合した結果です。", note)
    dashboard.write_row(3, 0, ["指標", "値"], header)
    kpis = model["kpis"]
    store_last_row = 4 + len(model["stores"])
    metrics = [
        ("商品売上", f"=SUM(Store!B5:B{store_last_row})", kpis["product_sales"]),
        ("返品商品金額", f"=SUM(Store!C5:C{store_last_row})", kpis["refund_product_amount"]),
        ("純商品売上", "=B5-B6", kpis["net_product_sales"]),
        ("販売数量", f"=SUM(Store!E5:E{store_last_row})", kpis["sales_quantity"]),
        ("返品数量", f"=SUM(Store!F5:F{store_last_row})", kpis["refund_quantity"]),
        ("純販売数量", "=B8-B9", kpis["net_quantity"]),
        ("注文数", f"=SUM(Store!H5:H{store_last_row})", kpis["completed_orders"]),
        ("合計請求額", f"=SUM(Store!I5:I{store_last_row})", kpis["total_billed"]),
        ("値引額", f"=SUM(Store!J5:J{store_last_row})", kpis["discount"]),
        ("送料", f"=SUM(Store!K5:K{store_last_row})", kpis["shipping"]),
        ("消費税額", f"=SUM(Store!L5:L{store_last_row})", kpis["tax"]),
    ]
    for row_index, (label, formula, value) in enumerate(metrics, 4):
        dashboard.write(row_index, 0, label)
        dashboard.write_formula(
            row_index,
            1,
            formula,
            integer if label in ("販売数量", "返品数量", "純販売数量", "注文数") else money,
            value,
        )
    dashboard.set_column("A:A", 18)
    dashboard.set_column("B:B", 16)

    monthly_chart = workbook.add_chart({"type": "line"})
    monthly_chart.add_series(
        {
            "name": "商品売上",
            "categories": f'=Monthly!$A$5:$A${4 + len(model["monthly"])}',
            "values": f'=Monthly!$B$5:$B${4 + len(model["monthly"])}',
            "line": {"color": "#2563EB", "width": 2.25},
        }
    )
    monthly_chart.set_title({"name": "月別商品売上推移"})
    monthly_chart.set_y_axis({"num_format": "¥#,##0", "major_gridlines": {"visible": True}})
    monthly_chart.set_legend({"none": True})
    monthly_chart.set_style(10)
    monthly_chart.set_size({"width": 610, "height": 260})
    dashboard.insert_chart("D4", monthly_chart)

    store_chart = workbook.add_chart({"type": "column"})
    store_chart.add_series(
        {
            "name": "商品売上",
            "categories": f'=Store!$A$5:$A${4 + len(model["stores"])}',
            "values": f'=Store!$B$5:$B${4 + len(model["stores"])}',
            "fill": {"color": "#0F766E"},
            "border": {"none": True},
        }
    )
    store_chart.set_title({"name": "店舗別商品売上"})
    store_chart.set_y_axis(
        {"min": 0, "num_format": "¥#,##0", "major_gridlines": {"visible": True}}
    )
    store_chart.set_legend({"none": True})
    store_chart.set_style(10)
    store_chart.set_size({"width": 610, "height": 260})
    dashboard.insert_chart("D18", store_chart)

    quality_sheet = sheets["Data_Quality"]
    quality_sheet.write("A1", "データ品質", title)
    quality_sheet.write_row(3, 0, ["項目", "件数"], header)
    quality = model["quality"]
    quality_values = [
        ("入力総件数", quality["input_rows"]),
        ("正常", quality["accepted_rows"]),
        ("要確認", quality["rejected_rows"]),
        ("除外（重複）", quality["excluded_duplicate_rows"]),
    ]
    for row_index, item in enumerate(quality_values, 4):
        quality_sheet.write(row_index, 0, item[0])
        quality_sheet.write_number(row_index, 1, item[1], integer)
    quality_sheet.write("A10", "照合結果")
    quality_sheet.write("B10", "OK" if quality["reconciliation_ok"] else "要確認")
    quality_sheet.set_column("A:A", 22)
    quality_sheet.set_column("B:B", 14)

    readme = sheets["README"]
    readme.write("A1", "このレポートについて", title)
    notes = [
        ("目的", "形式の異なる3店舗の架空売上CSVを共通形式へ変換・検証・集計するデモです。"),
        ("販売数量", "completed の quantity 合計。"),
        ("返品数量", "refunded の quantity 合計を正数表示。"),
        ("純販売数量", "販売数量 - 返品数量。"),
        ("注文数", "completed の注文IDを店舗内で重複除外した件数。行数ではありません。"),
        ("キャンセル", "Canonical Dataには保持し、主要販売KPIから除外。"),
        ("商品売上", "completed の商品金額合計。"),
        ("返品商品金額", "refunded の商品金額合計。"),
        ("純商品売上", "商品売上 - 返品商品金額。"),
        ("金額", "値引・送料・消費税・合計請求額を分離。返品は集計時に差し引きます。"),
        ("税率", "通常サンプルは10%と8%。1%は2027年4月以降の制度変更を想定した別テストケース。"),
        ("集計関係", "Monthly・Store・Product・TaxはClean_Dataを参照し、DashboardはStore集計を参照します。"),
        ("Data Quality", "入力総件数 = 正常 + 要確認 + 除外（重複）を確認します。"),
        ("会計CSV", "DEMO形式です。実案件ではお客様の取込仕様に合わせてカスタマイズします。"),
        ("免責", "本ツールは税務申告・会計判断ソフトではありません。"),
    ]
    readme.write_row(3, 0, ["項目", "説明"], header)
    for row_index, item in enumerate(notes, 4):
        readme.write_row(row_index, 0, item)
    readme.set_column("A:A", 18)
    readme.set_column("B:B", 90)

    workbook.close()
    return buffer.getvalue()
