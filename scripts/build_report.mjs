import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const args = process.argv.slice(2);
const getArg = (name, fallback) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
};

const modelPath = getArg("--model", "output/report_model.json");
const outputPath = getArg("--output", "output/ec_sales_report.xlsx");
const locale = getArg("--locale", "en");
if (!new Set(["en", "ja"]).has(locale)) throw new Error(`Unsupported locale: ${locale}`);
const model = JSON.parse(await fs.readFile(modelPath, "utf8"));

const messages = {
  en: {
    sheets: ["Summary", "Monthly", "By_Channel", "By_Product", "Clean_Data", "Data_Quality", "Run_Info"],
    summaryTitle: "EC sales summary", summarySub: "Synthetic data for North Market, Sakura Mall and Harbor Shop | JPY",
    metric: "Metric", value: "Value", netSales: "Net sales", orders: "Completed orders", units: "Units", aov: "Average order value",
    latestMonth: "Latest month", mom: "Month-over-month", dataQuality: "Data quality", inputRows: "Input rows", accepted: "Accepted", duplicates: "Duplicates", rejected: "Rejected",
    reconciled: "Reconciled", review: "Review required", monthlyTitle: "Monthly sales", monthlySub: "Net sales and units by local calendar month | JPY", month: "Month", monthlyChart: "Net sales by month",
    channelTitle: "Sales by channel", channelSub: "Completed and refunded transactions; cancelled rows contribute zero | JPY", channel: "Channel", channelChart: "Net sales by channel",
    productTitle: "Sales by product", productSub: "Products ranked by net sales | JPY", productId: "Product ID", product: "Product", productChart: "Top products by net sales",
    cleanTitle: "Clean data", cleanSub: "Normalized accepted rows with source lineage", qualityTitle: "Data quality", qualitySub: "Every source row is accepted, excluded as a duplicate, or rejected",
    measure: "Measure", duplicateRows: "Excluded duplicate rows", rejectedRows: "Rejected rows", reconciliation: "Reconciliation", sourceFile: "Source file", row: "Row", reason: "Reason", detail: "Detail",
    runTitle: "Run information", runSub: "Input provenance and configuration", property: "Property", contractVersion: "Contract version", toolVersion: "Tool version", inputFile: "Input file", source: "Source", rows: "Rows",
  },
  ja: {
    sheets: ["サマリー", "月別", "店舗別", "商品別", "統合データ", "データ品質", "実行情報"],
    summaryTitle: "EC売上サマリー", summarySub: "ノースマーケット、さくらモール、ハーバーショップの完全合成データ | 円",
    metric: "指標", value: "値", netSales: "純売上", orders: "完了注文数", units: "販売数量", aov: "平均注文単価",
    latestMonth: "最新月", mom: "前月比", dataQuality: "データ品質", inputRows: "入力行", accepted: "採用", duplicates: "重複", rejected: "不正",
    reconciled: "照合済み", review: "要確認", monthlyTitle: "月別売上", monthlySub: "日本時間の暦月による純売上と販売数量 | 円", month: "月", monthlyChart: "月別純売上",
    channelTitle: "店舗別売上", channelSub: "完了・返金取引を集計。キャンセル行は売上ゼロ | 円", channel: "店舗", channelChart: "店舗別純売上",
    productTitle: "商品別売上", productSub: "純売上の高い順 | 円", productId: "商品ID", product: "商品名", productChart: "商品別純売上",
    cleanTitle: "統合データ", cleanSub: "出典を追跡できる正規化済み採用行", qualityTitle: "データ品質", qualitySub: "全入力行を採用、重複、不正のいずれかに照合",
    measure: "項目", duplicateRows: "除外した重複行", rejectedRows: "不正行", reconciliation: "照合", sourceFile: "入力ファイル", row: "行", reason: "理由", detail: "詳細",
    runTitle: "実行情報", runSub: "入力ファイルの出典と設定", property: "項目", contractVersion: "契約バージョン", toolVersion: "ツールバージョン", inputFile: "入力ファイル", source: "店舗", rows: "行数",
  },
};
const m = messages[locale];
const channelJa = {"North Market": "ノースマーケット", "Sakura Mall": "さくらモール", "Harbor Shop": "ハーバーショップ"};
const productJa = {"Canvas Tote": "キャンバストート", "Ceramic Mug": "陶器マグ", "Desk Tray": "デスクトレー", "Linen Pouch": "リネンポーチ"};
const canonicalJa = {source_channel: "店舗", source_file: "入力ファイル", source_row: "入力行", order_id: "注文ID", order_date: "注文日", order_status: "注文状態", product_id: "商品ID", product_name: "商品名", quantity: "数量", unit_price: "単価", discount_amount: "値引額", shipping_amount: "送料", tax_amount: "税額", gross_sales: "総売上", net_sales: "純売上", currency: "通貨"};
const localChannel = (value) => locale === "ja" ? (channelJa[value] ?? value) : value;
const localProduct = (value) => locale === "ja" ? (productJa[value] ?? value) : value;
const localStatus = (value) => locale === "ja" ? ({completed: "完了", cancelled: "キャンセル", refunded: "返金"}[value] ?? value) : value;
const workbook = Workbook.create();
const [summaryName, monthlyName, channelName, productName, cleanName, qualityName, runInfoName] = m.sheets;
const summary = workbook.worksheets.add(summaryName);
const monthly = workbook.worksheets.add(monthlyName);
const channels = workbook.worksheets.add(channelName);
const products = workbook.worksheets.add(productName);
const clean = workbook.worksheets.add(cleanName);
const quality = workbook.worksheets.add(qualityName);
const runInfo = workbook.worksheets.add(runInfoName);

const navy = "#183B56";
const paleAmber = "#FFF2CC";
const paleRed = "#FCE4D6";
const dark = "#1F2937";
const lightLine = "#D9E2F3";
const font = "Arial";

function title(sheet, text, subtitle) {
  sheet.showGridLines = false;
  sheet.getRange("A1:H1").format.borders = { bottom: { style: "thin", color: navy } };
  sheet.getRange("A1").values = [[text]];
  sheet.getRange("A1").format.font = { name: font, size: 16, bold: true, color: navy };
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange("A2:H2").format.font = { name: font, size: 9, italic: true, color: "#5B6573" };
}

function header(range) {
  range.format.fill = navy;
  range.format.font = { name: font, size: 10, bold: true, color: "#FFFFFF" };
  range.format.horizontalAlignment = "center";
  range.format.verticalAlignment = "center";
}

function body(range) {
  range.format.font = { name: font, size: 10, color: dark };
  range.format.borders = { insideHorizontal: { style: "thin", color: lightLine } };
}

title(summary, m.summaryTitle, m.summarySub);
summary.getRange("A4:B8").values = [
  [m.metric, m.value],
  [m.netSales, model.kpis.net_sales],
  [m.orders, model.kpis.completed_orders],
  [m.units, model.kpis.units],
  [m.aov, model.kpis.average_order_value],
];
summary.getRange("D4:E5").values = [[m.latestMonth, m.mom], [model.monthly.at(-1)?.month ?? "", model.kpis.latest_mom_change]];
header(summary.getRange("A4:B4"));
header(summary.getRange("D4:E4"));
body(summary.getRange("A5:B8"));
body(summary.getRange("D5:E5"));
summary.getRange("B5").setNumberFormat('¥#,##0;[Red]-¥#,##0');
summary.getRange("B8").setNumberFormat('¥#,##0;[Red]-¥#,##0');
summary.getRange("E5").setNumberFormat("0.0%;[Red]-0.0%");
summary.getRange("A10:E11").values = [[m.dataQuality, m.inputRows, m.accepted, m.duplicates, m.rejected], [model.quality.reconciliation_ok ? m.reconciled : m.review, model.quality.input_rows, model.quality.accepted_rows, model.quality.excluded_duplicate_rows, model.quality.rejected_rows]];
header(summary.getRange("A10:E10"));
body(summary.getRange("A11:E11"));
summary.getRange("A11").format.fill = model.quality.reconciliation_ok ? "#E2F0D9" : paleRed;
summary.getRange("A:A").format.columnWidth = 24;
summary.getRange("B:B").format.columnWidth = 16;
summary.getRange("C:C").format.columnWidth = 14;
summary.getRange("D:E").format.columnWidth = 18;

title(monthly, m.monthlyTitle, m.monthlySub);
const monthlyRows = model.monthly.map((row) => [row.month, row.net_sales, row.units, row.mom_change]);
monthly.getRange("A4:D4").values = [[m.month, m.netSales, m.units, m.mom]];
if (monthlyRows.length) monthly.getRangeByIndexes(4, 0, monthlyRows.length, 4).values = monthlyRows;
header(monthly.getRange("A4:D4"));
body(monthly.getRangeByIndexes(4, 0, Math.max(monthlyRows.length, 1), 4));
monthly.getRange(`B5:B${4 + monthlyRows.length}`).setNumberFormat('¥#,##0;[Red]-¥#,##0');
monthly.getRange(`D5:D${4 + monthlyRows.length}`).setNumberFormat("0.0%;[Red]-0.0%");
monthly.getRange("A:D").format.columnWidth = 18;
if (monthlyRows.length) {
  const chart = monthly.charts.add("line", monthly.getRange(`A4:B${4 + monthlyRows.length}`));
  chart.titleText = m.monthlyChart;
  chart.hasLegend = false;
  chart.setPosition("F4", "M18");
}

title(channels, m.channelTitle, m.channelSub);
const channelRows = model.channels.map((row) => [localChannel(row.channel), row.net_sales, row.orders, row.units]);
channels.getRange("A4:D4").values = [[m.channel, m.netSales, m.orders, m.units]];
channels.getRangeByIndexes(4, 0, channelRows.length, 4).values = channelRows;
header(channels.getRange("A4:D4"));
body(channels.getRangeByIndexes(4, 0, channelRows.length, 4));
channels.getRange(`B5:B${4 + channelRows.length}`).setNumberFormat('¥#,##0;[Red]-¥#,##0');
channels.getRange("A:A").format.columnWidth = 22;
channels.getRange("B:D").format.columnWidth = 18;
const channelChart = channels.charts.add("bar", channels.getRange(`A4:B${4 + channelRows.length}`));
channelChart.titleText = m.channelChart;
channelChart.hasLegend = false;
channelChart.setPosition("F4", "M18");

title(products, m.productTitle, m.productSub);
const productRows = model.products.map((row) => [row.product_id, localProduct(row.product_name), row.net_sales, row.units]);
products.getRange("A4:D4").values = [[m.productId, m.product, m.netSales, m.units]];
products.getRangeByIndexes(4, 0, productRows.length, 4).values = productRows;
header(products.getRange("A4:D4"));
body(products.getRangeByIndexes(4, 0, productRows.length, 4));
products.getRange(`C5:C${4 + productRows.length}`).setNumberFormat('¥#,##0;[Red]-¥#,##0');
products.getRange("A:A").format.columnWidth = 14;
products.getRange("B:B").format.columnWidth = 24;
products.getRange("C:D").format.columnWidth = 16;
const productChart = products.charts.add("bar", products.getRange(`B4:C${4 + productRows.length}`));
productChart.titleText = m.productChart;
productChart.hasLegend = false;
productChart.setPosition("F4", "M19");

title(clean, m.cleanTitle, m.cleanSub);
const cleanHeaders = Object.keys(model.clean_data[0] ?? {});
const cleanRows = model.clean_data.map((row) => cleanHeaders.map((key) => key === "source_channel" ? localChannel(row[key]) : key === "product_name" ? localProduct(row[key]) : key === "order_status" ? localStatus(row[key]) : row[key]));
clean.getRangeByIndexes(3, 0, 1, cleanHeaders.length).values = [cleanHeaders.map((key) => locale === "ja" ? canonicalJa[key] : key)];
if (cleanRows.length) clean.getRangeByIndexes(4, 0, cleanRows.length, cleanHeaders.length).values = cleanRows;
header(clean.getRangeByIndexes(3, 0, 1, cleanHeaders.length));
body(clean.getRangeByIndexes(4, 0, Math.max(cleanRows.length, 1), cleanHeaders.length));
clean.freezePanes.freezeRows(4);
clean.getRange("A:P").format.columnWidth = 16;
clean.getRange("D:D").format.columnWidth = 14;
clean.getRange("H:H").format.columnWidth = 22;
clean.getRange(`J5:O${4 + cleanRows.length}`).setNumberFormat('¥#,##0;[Red]-¥#,##0');

title(quality, m.qualityTitle, m.qualitySub);
quality.getRange("A4:B9").values = [[m.measure, m.value], [m.inputRows, model.quality.input_rows], [m.accepted, model.quality.accepted_rows], [m.duplicateRows, model.quality.excluded_duplicate_rows], [m.rejectedRows, model.quality.rejected_rows], [m.reconciliation, model.quality.reconciliation_ok ? "OK" : m.review]];
header(quality.getRange("A4:B4"));
body(quality.getRange("A5:B9"));
quality.getRange("A11:D11").values = [[m.sourceFile, m.row, m.reason, m.detail]];
header(quality.getRange("A11:D11"));
const rejectionRows = model.quality.rejections.map((row) => [row.source_file, row.source_row, locale === "ja" && row.reason === "invalid_row" ? "不正行" : row.reason, locale === "ja" ? row.detail.replace("invalid quantity", "数量が不正です") : row.detail]);
if (rejectionRows.length) {
  quality.getRangeByIndexes(11, 0, rejectionRows.length, 4).values = rejectionRows;
  quality.getRangeByIndexes(11, 0, rejectionRows.length, 4).format.fill = paleAmber;
  body(quality.getRangeByIndexes(11, 0, rejectionRows.length, 4));
}
quality.getRange("A:A").format.columnWidth = 28;
quality.getRange("B:B").format.columnWidth = 16;
quality.getRange("C:C").format.columnWidth = 18;
quality.getRange("D:D").format.columnWidth = 48;

title(runInfo, m.runTitle, m.runSub);
runInfo.getRange("A4:B6").values = [[m.property, m.value], [m.contractVersion, model.quality.contract_version], [m.toolVersion, "0.1.0"]];
header(runInfo.getRange("A4:B4"));
body(runInfo.getRange("A5:B6"));
runInfo.getRange("A8:D8").values = [[m.inputFile, m.source, m.rows, "SHA-256"]];
header(runInfo.getRange("A8:D8"));
const fileRows = model.quality.files.map((row) => [row.name, localChannel(row.source), row.rows, row.sha256]);
runInfo.getRangeByIndexes(8, 0, fileRows.length, 4).values = fileRows;
body(runInfo.getRangeByIndexes(8, 0, fileRows.length, 4));
runInfo.getRange("A:A").format.columnWidth = 30;
runInfo.getRange("B:B").format.columnWidth = 20;
runInfo.getRange("C:C").format.columnWidth = 10;
runInfo.getRange("D:D").format.columnWidth = 68;

for (const sheet of [summary, monthly, channels, products, clean, quality, runInfo]) {
  sheet.getUsedRange()?.format.autofitRows();
}

const summaryCheck = await workbook.inspect({kind: "table", range: `${summaryName}!A1:E11`, include: "values,formulas", tableMaxRows: 20, tableMaxCols: 8});
console.log(summaryCheck.ndjson);
const errors = await workbook.inspect({kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: {useRegex: true, maxResults: 300}, summary: "final formula error scan"});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputPath), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const previewDir = path.join(path.dirname(outputPath), `${path.basename(outputPath, ".xlsx")}.previews`);
await fs.mkdir(previewDir, { recursive: true });
for (const sheetName of m.sheets) {
  const preview = await workbook.render({sheetName, autoCrop: "all", scale: 1, format: "png"});
  await fs.writeFile(path.join(previewDir, `${sheetName}.png`), new Uint8Array(await preview.arrayBuffer()));
}
console.log(JSON.stringify({outputPath, previewDir}));
