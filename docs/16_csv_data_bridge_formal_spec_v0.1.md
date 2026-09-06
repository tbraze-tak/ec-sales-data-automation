# Portfolio #1 正式仕様書 v0.1

## CSV Data Bridge

### 複数店舗の売上データを一括集計

Version: v0.1

Status: Formal Specification

Project: Team ARGO Portfolio #1

Purpose: CrowdWorks等の副業案件へ提示可能なPortfolio成果物

Data Classification: 完全架空データのみ

Language: 日本語

Currency: JPY

---

## 1. 目的

本Portfolioの目的は、

「形式の異なる複数の売上CSVを、一定のデータモデルへ正規化し、検証・集計・レポート生成まで自動化できること」

を実演することである。

Portfolioそのものを制作することが最終目的ではない。

本Portfolioは、

- CSV整理
- CSV変換
- データクレンジング
- Excel集計
- Excelレポート作成
- データ検証
- 小規模業務自動化

等の案件について、Team ARGOが

- 要件を整理できる
- データ構造を設計できる
- 実装できる
- テストできる
- 独立検証できる
- 顧客へ説明できる

ことを示すための実績サンプルとする。

---

## 2. 顧客向け名称

メインタイトル：

複数店舗の売上データを一括集計

サブタイトル：

CSV Data Bridge — 売上CSV自動変換デモ

---

## 3. 絶対安全条件

本Portfolioでは勤務先および本業に関連する情報を一切使用しない。

以下は禁止する。

- EVバス
- CAN
- BMS
- OBC
- VCU
- 車両故障解析
- 会社ログ
- DBC
- 社内仕様書
- 社内コード
- 社内レポート
- 顧客データ
- 非公開故障事例
- 勤務先固有ノウハウ
- その他勤務先の非公開情報

匿名化・加工した勤務先データの使用も禁止する。

サンプルデータはすべて、Team ARGOがゼロから生成した完全架空データとする。

---

## 4. 処理フロー

```text
Input
↓
Normalize
↓
Validate
↓
Canonical Data
↓
Process
↓
Output
```

入力形式依存処理と集計ロジックを可能な限り分離する。

---

## 5. 架空店舗

- North Market
- Sakura Mall
- Harbor Shop

3店舗とも完全架空店舗。

異なるCSVフォーマットを意図的に使用する。

---

## 6. Canonical Data v0.1

最低限：

- store
- order_id
- order_date
- year_month
- status
- sku
- product_name
- quantity
- unit_price
- gross_item_amount
- discount_amount
- shipping_amount
- tax_category
- tax_rate
- tax_amount
- total_amount
- source_file

必要なら：

- currency = JPY

---

## 7. Canonical Data原則

Canonical Dataでは元入力データの意味を保持する。

refundについて、元CSV：

```text
status = refunded
quantity = 1
```

の場合、Canonicalでも：

```text
status = refunded
quantity = 1
```

とする。

`quantity = -1`へ変換してはならない。

返品としての差引処理は集計側で行う。

cancelledも削除しない。

```text
status = cancelled
```

としてCanonicalへ保持し、主要販売KPIの集計対象から除外する。

---

## 8. 数量定義

販売数量：

completedのquantity合計

返品数量：

refundedのquantity合計

返品数量は正数表示。

純販売数量：

販売数量 - 返品数量

cancelled数量：

主要販売KPIには含めない。

---

## 9. 金額定義

gross_item_amount：

quantity × unit_price

discount_amount：

元CSVの値引額

shipping_amount：

元CSVの送料

tax_amount：

元CSVまたは明示されたサンプル生成仕様上の税額

total_amount：

顧客への最終請求額

元CSVにtotal_amountがない現在のサンプルでは、

```text
gross_item_amount
- discount_amount
+ shipping_amount
+ tax_amount
```

で算出可能。

ただし一般的な税務・会計ルールとして説明しない。

---

## 10. 商品売上定義

商品売上：

completedの商品金額合計

返品商品金額：

refundedの商品金額合計

純商品売上：

商品売上 - 返品商品金額

---

## 11. 「純売上」名称

以下の曖昧な名称はv0.1では廃止する。

- net_sales
- 純売上

送料・消費税等を含む金額を「純売上」と呼ばない。

代わりに、

- 商品売上
- 返品商品金額
- 純商品売上
- 値引額
- 送料
- 消費税額
- 合計請求額

等の意味が明確な名称を使用する。

---

## 12. 国内消費税

通常サンプル：

- 10% 標準税率
- 8% 軽減税率

---

## 13. 将来テストケース

別データとして、

「2027年4月以降の制度変更を想定した飲食料品1%」

をテストケースとして持つ。

重要：

- 現行制度として説明しない
- 2025～2026年通常取引へ混在させない
- 将来ケースとして分離する
- 実案件では適用時点の法令・顧客仕様を確認する

---

## 14. 税率設計

Canonical Dataへ、

- tax_category
- tax_rate
- tax_amount

を持つ。

例：

```text
standard / 0.10
reduced / 0.08
future_food / 0.01
```

商品名だけから税率を推測しない。

商品マスタ等へ明示的に税区分を設定する。

税率変更に対応できるよう、税率を不用意に処理ロジックへベタ書きしない。

---

## 15. サンプルデータ

最低限：

1. 通常販売 10%
2. 値引あり 10%
3. 送料あり 10%
4. 飲食料品 8%
5. キャンセル 10%
6. 返金 10%
7. 返金 8%

別テスト：

8. 2027年4月以降想定・飲食料品1%

必要なら既存CSVへ継ぎ足すのではなく、

```text
商品マスタ
↓
税区分
↓
取引生成
↓
税額生成
↓
3店舗形式生成
```

で再生成する。

---

## 16. 出力

1. 統合・クリーンCSV
2. Excel売上レポート
3. 会計システム取込CSV（DEMO）

会計CSV：

「DEMO形式です。実案件ではお客様の取込仕様に合わせてカスタマイズします。」

と明記。

実在会計ソフトとの正式互換性は主張しない。

---

## 17. Excel

`sales_report.xlsx`

必須シート：

- Dashboard
- Monthly
- Store
- Product
- Tax
- Clean_Data
- Data_Quality
- README

---

## 18. Dashboard

主要KPI：

- 商品売上
- 販売数量
- 返品数量
- 純販売数量
- 注文数
- 合計請求額

補足：

- 値引額
- 送料
- 消費税額

「純売上」は使用しない。

---

## 19. Tax

最低限：

- 税率
- 税区分
- 対象商品売上
- 値引額
- 税額
- 取引数

通常：

- 10%
- 8%

1%は将来想定として明記する。

---

## 20. README

日本語で最低限、

- Portfolioの目的
- 販売数量
- 返品数量
- 純販売数量
- キャンセル
- 商品売上
- 返品商品金額
- 純商品売上
- 値引
- 送料
- 消費税
- 合計請求額
- 10%
- 8%
- 将来想定1%
- Data Quality
- DEMO会計CSV
- 税務申告・会計判断ソフトではない

ことを説明する。

---

## 21. Streamlit UI

Screen 1：説明

Screen 2：操作

説明と操作を同一画面へ混在させない。

Screen 1：

タイトル：

複数店舗の売上データを一括集計

サブタイトル：

CSV Data Bridge — 売上CSV自動変換デモ

「では、実際にやってみましょう」

「デモを試してみる」

という導線を設ける。

---

## 22. 元CSVプレビュー

説明画面から、

「実際のサンプルデータを見る」

を選択できる。

3タブ：

- North Market 売上表
- Sakura Mall 売上表
- Harbor Shop 売上表

各CSV先頭10行程度を、加工せず元データのまま表示する。

---

## 23. 任意CSVアップロード

v0.1では禁止。

Team ARGOが準備・検証した3店舗サンプルだけ使用する。

「どんなCSVでも変換可能」と誤認される機能・表現を避ける。

表現：

「登録された入力形式を自動判別」

---

## 24. Data Quality

`quality["rejected_rows"]`等、既存内部値の意味はコード・テストから確認する。

推測で意味を変更しない。

UI表示：

- 正常
- 要確認
- 除外

等と内部データの対応を明確化する。

入力総件数との数学的整合性を確認する。

---

## 25. Team ARGO独立QA

CodexのテストPASSだけでは公開しない。

最低限：

- 通常販売
- 値引
- 送料
- 10%
- 8%
- キャンセル
- 10%返金
- 8%返金
- 1%将来ケース

を確認する。

```text
元CSV
↓
Canonical
↓
Clean CSV
↓
Excel
↓
Dashboard
```

まで、1円・1個単位で追跡できること。

---

## 26. QA数式

```text
販売数量
= completed quantity合計

返品数量
= refunded quantity合計

純販売数量
= 販売数量 - 返品数量

商品売上
= completed商品金額合計

返品商品金額
= refunded商品金額合計

純商品売上
= 商品売上 - 返品商品金額

税率別税額合計
= 全体税額合計

Monthly
Store
Product
Tax
の合計
= Dashboard
```

---

## 27. 公開合格基準

以下すべて必須。

- 架空データのみ
- 勤務先情報ゼロ
- 3CSV仕様を説明可能
- Canonical Modelを説明可能
- refundの意味を壊していない
- cancelledを正しく保持・除外
- 「純売上」の誤表示なし
- 10% / 8%を正しく保持
- 1%将来ケースを明確に分離
- Excel KPI定義が明確
- Dashboardと各集計一致
- 元CSVからExcelまで追跡可能
- 元CSVプレビュー動作
- 任意CSVアップロードなし
- 会計ソフト互換性を誤認させない
- 全テストPASS
- Team ARGO独立QA PASS

---

## 28. 非目標

v0.1では、

- あらゆるCSVへの自動対応
- 任意CSV解析
- 実在会計ソフト完全互換
- 税務申告
- 会計判断
- ERP
- POS
- EC基幹システム

等を目的としない。

---

## 29. 品質原則

案件・Portfolio共通の最重要基準：

「Team ARGO自身で成果物を独立検証・デバッグできるか？」

AIがコードを生成できるだけでは不十分。

- 原因を理解できる
- 再現できる
- テストできる
- 修正できる
- 納品品質を説明できる

ことを必要条件とする。

---

## 30. v0.1完了条件

1. 本仕様を正本へ登録
2. 実装を本仕様へ整合
3. サンプルデータを整合
4. 自動テストPASS
5. Excel検証PASS
6. Streamlit動作確認PASS
7. Team ARGO独立QA PASS
8. 公開判定PASS

その後、CrowdWorks実案件応募へ進む。
