from __future__ import annotations

import io
from datetime import datetime

import xlsxwriter

from ec_sales.bridge import BRIDGE_COLUMNS, canonical_rows


def build_excel_report(model: dict) -> bytes:
    """Build a Japanese-first, formula-linked Excel report."""
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
    workbook.set_properties({
        "title": "CSV Data Bridge 売上レポート",
        "comments": "完全合成データによるデモレポート",
    })

    navy = "#17324D"
    blue = "#2F75B5"
    pale = "#EAF2F8"
    gray = "#64748B"
    green = "#15803D"
    red = "#B91C1C"
    title = workbook.add_format({"bold": True, "font_size": 18, "font_color": navy})
    subtitle = workbook.add_format({"font_color": gray, "italic": True})
    header = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": navy, "align": "center", "valign": "vcenter"})
    section = workbook.add_format({"bold": True, "font_color": navy, "bg_color": pale})
    integer = workbook.add_format({"num_format": "#,##0"})
    currency = workbook.add_format({"num_format": '¥#,##0;[Red]-¥#,##0'})
    percent = workbook.add_format({"num_format": "0.0%"})
    date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd"})
    ok_fmt = workbook.add_format({"bold": True, "font_color": green})
    error_fmt = workbook.add_format({"font_color": red})

    sheets = {}
    for name in ("Dashboard", "Monthly", "Channel", "Product", "Clean_Data", "Data_Quality", "README"):
        sheets[name] = workbook.add_worksheet(name)
        sheets[name].hide_gridlines(2)

    rows = canonical_rows(model)
    clean = sheets["Clean_Data"]
    clean.freeze_panes(4, 3)
    clean.write("A1", "Canonical Clean Data", title)
    clean.write("A2", "全集計シートの計算元。金額列は行内の数式で再計算されます。", subtitle)
    clean_headers = BRIDGE_COLUMNS + ["order_count_flag"]
    clean.write_row(3, 0, clean_headers, header)
    for index, row in enumerate(rows, start=4):
        excel_row = index + 1
        values = [row[column] for column in BRIDGE_COLUMNS]
        for column, value in enumerate(values):
            if column == 2:
                clean.write_datetime(index, column, datetime.fromisoformat(str(value)), date_fmt)
            elif column in (7,):
                clean.write_number(index, column, value, integer)
            elif column in (8, 9, 10, 11, 12, 13):
                clean.write_number(index, column, value, currency)
            else:
                clean.write(index, column, value)
        clean.write_formula(index, 9, f'=IF(E{excel_row}="cancelled",0,H{excel_row}*I{excel_row})', currency, row["gross_sales"])
        clean.write_formula(index, 13, f"=J{excel_row}-K{excel_row}+L{excel_row}+M{excel_row}", currency, row["net_sales"])
        order_flag = 1 if row["status"] == "completed" and not any(
            earlier["status"] == "completed" and earlier["store"] == row["store"] and earlier["order_id"] == row["order_id"]
            for earlier in rows[: index - 4]
        ) else 0
        clean.write_formula(
            index,
            15,
            f'=IF(E{excel_row}<>"completed",0,--(COUNTIFS($A$5:A{excel_row},A{excel_row},$B$5:B{excel_row},B{excel_row},$E$5:E{excel_row},"completed")=1))',
            integer,
            order_flag,
        )
    end_row = 4 + len(rows)
    clean.add_table(3, 0, end_row - 1, len(clean_headers) - 1, {
        "name": "CleanDataTable",
        "style": "Table Style Medium 2",
        "columns": [{"header": name} for name in clean_headers],
    })
    clean.set_column("A:A", 18)
    clean.set_column("B:B", 15)
    clean.set_column("C:E", 13)
    clean.set_column("F:F", 12)
    clean.set_column("G:G", 22)
    clean.set_column("H:N", 13)
    clean.set_column("O:O", 25)
    clean.set_column("P:P", 17)

    monthly = sheets["Monthly"]
    monthly.write("A1", "月別売上", title)
    monthly.write("A2", "Clean_DataからSUMIFSで集計", subtitle)
    monthly.write_row("A4", ["月", "純売上", "販売数量", "前月比"], header)
    for offset, item in enumerate(model["monthly"], start=4):
        excel_row = offset + 1
        year, month = map(int, item["month"].split("-"))
        monthly.write(offset, 0, item["month"])
        monthly.write_formula(offset, 1, f'=SUMIFS(Clean_Data!$N$5:$N${end_row},Clean_Data!$D$5:$D${end_row},A{excel_row})', currency, item["net_sales"])
        monthly.write_formula(offset, 2, f'=SUMIFS(Clean_Data!$H$5:$H${end_row},Clean_Data!$D$5:$D${end_row},A{excel_row},Clean_Data!$E$5:$E${end_row},"<>cancelled")', integer, item["units"])
        if offset == 4:
            monthly.write_blank(offset, 3, None, percent)
        else:
            monthly.write_formula(offset, 3, f'=IFERROR(B{excel_row}/B{excel_row - 1}-1,"")', percent, item["mom_change"])
    monthly.set_column("A:A", 12)
    monthly.set_column("B:D", 14)
    month_chart = workbook.add_chart({"type": "line"})
    month_chart.add_series({"name": "純売上", "categories": f"=Monthly!$A$5:$A${4 + len(model['monthly'])}", "values": f"=Monthly!$B$5:$B${4 + len(model['monthly'])}", "line": {"color": blue, "width": 2.25}})
    month_chart.set_title({"name": "月別純売上"})
    month_chart.set_legend({"none": True})
    monthly.insert_chart("F4", month_chart, {"x_scale": 1.25, "y_scale": 1.1})

    channel = sheets["Channel"]
    channel.write("A1", "店舗別売上", title)
    channel.write("A2", "Clean_DataからSUMIFSで集計", subtitle)
    channel.write_row("A4", ["店舗", "純売上", "注文数", "販売数量"], header)
    for offset, item in enumerate(model["channels"], start=4):
        excel_row = offset + 1
        channel.write(offset, 0, item["channel"])
        channel.write_formula(offset, 1, f'=SUMIFS(Clean_Data!$N$5:$N${end_row},Clean_Data!$A$5:$A${end_row},A{excel_row})', currency, item["net_sales"])
        channel.write_formula(offset, 2, f'=SUMIFS(Clean_Data!$P$5:$P${end_row},Clean_Data!$A$5:$A${end_row},A{excel_row})', integer, item["orders"])
        channel.write_formula(offset, 3, f'=SUMIFS(Clean_Data!$H$5:$H${end_row},Clean_Data!$A$5:$A${end_row},A{excel_row},Clean_Data!$E$5:$E${end_row},"<>cancelled")', integer, item["units"])
    channel.set_column("A:A", 20)
    channel.set_column("B:D", 14)
    channel_chart = workbook.add_chart({"type": "column"})
    channel_chart.add_series({"name": "純売上", "categories": f"=Channel!$A$5:$A${4 + len(model['channels'])}", "values": f"=Channel!$B$5:$B${4 + len(model['channels'])}", "fill": {"color": blue}})
    channel_chart.set_title({"name": "店舗別純売上"})
    channel_chart.set_legend({"none": True})
    channel.insert_chart("F4", channel_chart, {"x_scale": 1.25, "y_scale": 1.1})

    product = sheets["Product"]
    product.write("A1", "商品別売上", title)
    product.write("A2", "Clean_DataからSUMIFSで集計", subtitle)
    product.write_row("A4", ["SKU", "商品名", "純売上", "販売数量"], header)
    for offset, item in enumerate(model["products"], start=4):
        excel_row = offset + 1
        product.write_row(offset, 0, [item["product_id"], item["product_name"]])
        product.write_formula(offset, 2, f'=SUMIFS(Clean_Data!$N$5:$N${end_row},Clean_Data!$F$5:$F${end_row},A{excel_row})', currency, item["net_sales"])
        product.write_formula(offset, 3, f'=SUMIFS(Clean_Data!$H$5:$H${end_row},Clean_Data!$F$5:$F${end_row},A{excel_row},Clean_Data!$E$5:$E${end_row},"<>cancelled")', integer, item["units"])
    product.set_column("A:A", 12)
    product.set_column("B:B", 24)
    product.set_column("C:D", 14)
    top_count = min(5, len(model["products"]))
    product_chart = workbook.add_chart({"type": "bar"})
    product_chart.add_series({"name": "純売上", "categories": f"=Product!$B$5:$B${4 + top_count}", "values": f"=Product!$C$5:$C${4 + top_count}", "fill": {"color": blue}})
    product_chart.set_title({"name": "商品売上 TOP5"})
    product_chart.set_legend({"none": True})
    product.insert_chart("F4", product_chart, {"x_scale": 1.25, "y_scale": 1.1})

    dashboard = sheets["Dashboard"]
    dashboard.write("A1", "CSV Data Bridge 売上ダッシュボード", title)
    dashboard.write("A2", "すべてのKPIは集計シートまたはClean_Dataを参照", subtitle)
    dashboard.write_row("A4", ["指標", "値"], header)
    dashboard.write_column("A5", ["総売上", "注文数", "販売数量", "平均注文単価", "対象期間"])
    dashboard.write_formula("B5", f"=SUM(Monthly!B5:B{4 + len(model['monthly'])})", currency, model["kpis"]["net_sales"])
    dashboard.write_formula("B6", f"=SUM(Channel!C5:C{4 + len(model['channels'])})", integer, model["kpis"]["completed_orders"])
    dashboard.write_formula("B7", f"=SUM(Monthly!C5:C{4 + len(model['monthly'])})", integer, model["kpis"]["units"])
    dashboard.write_formula("B8", '=IFERROR(B5/B6,"")', currency, model["kpis"]["average_order_value"])
    period = f'{model["monthly"][0]["month"]} ～ {model["monthly"][-1]["month"]}' if model["monthly"] else "対象データなし"
    dashboard.write("B9", period)
    dashboard.write("A11", "集計整合性", section)
    dashboard.write_formula("B11", f'=IF(AND(B5=SUM(Channel!B5:B{4 + len(model["channels"])}),B5=SUM(Product!C5:C{4 + len(model["products"])}),B5=SUM(Clean_Data!N5:N{end_row})),"OK","要確認")', ok_fmt, "OK")
    dashboard.set_column("A:A", 18)
    dashboard.set_column("B:B", 22)

    quality = sheets["Data_Quality"]
    quality.write("A1", "データ品質", title)
    quality.write("A2", "正常・要確認・除外の件数と詳細", subtitle)
    quality.write_row("A4", ["項目", "件数"], header)
    quality.write_column("A5", ["入力行", "正常", "要確認", "除外", "ファイルエラー"])
    q = model["quality"]
    for row_index, value in enumerate([q["input_rows"], q["accepted_rows"], q["rejected_rows"], q["excluded_duplicate_rows"], len(q["fatal_files"])], start=4):
        quality.write_number(row_index, 1, value, integer)
    quality.write_row("A12", ["Issue Type", "Source File", "Row", "Order ID", "Description"], header)
    for offset, issue in enumerate(q["rejections"], start=12):
        quality.write_row(offset, 0, [issue["reason"], issue["source_file"], issue["source_row"], issue.get("order_id", ""), issue["detail"]], error_fmt)
    for fatal_index, issue in enumerate(q["fatal_files"], start=12 + len(q["rejections"])):
        quality.write_row(fatal_index, 0, ["FILE_ERROR", issue["name"], "", "", issue["error"]], error_fmt)
    quality.set_column("A:A", 18)
    quality.set_column("B:B", 28)
    quality.set_column("C:C", 10)
    quality.set_column("D:D", 16)
    quality.set_column("E:E", 60)

    readme = sheets["README"]
    readme.write("A1", "このレポートについて", title)
    notes = [
        ["目的", "複数形式のCSVを共通形式へ変換し、売上集計を確認するデモです。"],
        ["更新関係", "Dashboard、Monthly、Channel、ProductはClean_Dataを参照します。"],
        ["編集", "Clean_Dataの既存行を変更すると、数式とグラフが再計算されます。"],
        ["データ", "サンプルは完全合成データです。"],
        ["会計DEMO", "実在会計製品の正式仕様ではありません。実案件では取込仕様に合わせて調整します。"],
    ]
    readme.write_row("A4", ["項目", "説明"], header)
    readme.write_row("A5", notes[0])
    for index, note in enumerate(notes[1:], start=5):
        readme.write_row(index, 0, note)
    readme.set_column("A:A", 16)
    readme.set_column("B:B", 75)

    workbook.close()
    return buffer.getvalue()
