import csv, io, json, tempfile, unittest, zipfile
from pathlib import Path
from ec_sales.bridge import accounting_demo_bytes, clean_csv_bytes, identify_csv, process_uploads, zip_outputs
from ec_sales.output_adapters import build_excel_report
from ec_sales.pipeline import PipelineError, run_pipeline
ROOT=Path(__file__).resolve().parents[1]; CONTRACT=ROOT/'config'/'source_contracts.json'
class BridgeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with tempfile.TemporaryDirectory() as d: cls.model=run_pipeline(ROOT/'sample_data'/'input',Path(d),CONTRACT)
 def test_large_synthetic_sample_and_three_sources(self):
  q=self.model['quality']; self.assertEqual((q['input_rows'],q['accepted_rows'],q['excluded_duplicate_rows'],q['rejected_rows']),(1024,1022,1,1)); self.assertTrue(q['reconciliation_ok']); self.assertEqual(self.model['kpis']['sales_quantity'],2955); self.assertEqual(self.model['kpis']['refund_quantity'],28); self.assertEqual(self.model['kpis']['net_quantity'],2927); self.assertEqual({x['tax_rate'] for x in self.model['taxes']},{0.08,0.10})
  self.assertEqual(self.model['kpis']['product_sales'],8781775); self.assertEqual(self.model['kpis']['refund_product_amount'],87325); self.assertEqual(self.model['kpis']['net_product_sales'],8694450); self.assertEqual(self.model['kpis']['completed_orders'],986); self.assertEqual(self.model['kpis']['total_billed'],9619580)
  for dimension in ('monthly','stores','products','taxes'):
   self.assertEqual(sum(item['product_sales'] for item in self.model[dimension]),self.model['kpis']['product_sales']); self.assertEqual(sum(item['refund_product_amount'] for item in self.model[dimension]),self.model['kpis']['refund_product_amount']); self.assertEqual(sum(item['sales_quantity'] for item in self.model[dimension]),self.model['kpis']['sales_quantity']); self.assertEqual(sum(item['refund_quantity'] for item in self.model[dimension]),self.model['kpis']['refund_quantity']); self.assertEqual(sum(item['orders'] for item in self.model[dimension]),self.model['kpis']['completed_orders']); self.assertEqual(sum(item['total_billed'] for item in self.model[dimension]),self.model['kpis']['total_billed'])
 def test_refunds_preserve_positive_quantity(self):
  refunds=[r for r in self.model['clean_data'] if r['order_status']=='refunded']; self.assertTrue(refunds); self.assertTrue(all(r['quantity']>0 for r in refunds))
 def test_header_detection_does_not_require_filename(self):
  data=(ROOT/'sample_data/input/north_market_2026.csv').read_bytes(); r=identify_csv(data,'customer_export.csv',CONTRACT); self.assertEqual(r['source_key'],'north_market'); self.assertEqual(r['rows'],340)
 def test_uploaded_cp932_csv_is_normalized(self):
  text='注文番号,注文日,状態,商品コード,商品名,個数,販売単価\nS-1,2026/08/01,発送済,P-1,合成商品,1,1000\n'; self.assertEqual(identify_csv(text.encode('cp932'),'export.csv',CONTRACT)['source_key'],'sakura_mall')
 def test_unknown_schema_is_reported(self):
  with self.assertRaises(PipelineError): identify_csv(b'unknown,value\n1,2\n','unknown.csv',CONTRACT)
 def test_clean_csv_and_accounting_demo(self):
  clean=list(csv.DictReader(io.StringIO(clean_csv_bytes(self.model).decode('utf-8-sig')))); self.assertIn('gross_item_amount',clean[0]); self.assertNotIn('net_sales',clean[0]); acc=list(csv.DictReader(io.StringIO(accounting_demo_bytes(self.model).decode('utf-8-sig')))); self.assertEqual({r['tax_category'] for r in acc},{'DEMO_STANDARD_10PCT','DEMO_REDUCED_8PCT'}); self.assertEqual(sum(int(r['debit_amount']) for r in acc),self.model['kpis']['total_billed']); self.assertEqual(sum(int(r['credit_amount']) for r in acc),self.model['kpis']['total_billed']); self.assertEqual(sum(int(r['debit_amount'])<0 for r in acc),9)
 def test_excel_required_sheets(self):
  with zipfile.ZipFile(io.BytesIO(build_excel_report(self.model))) as z:
   wb=z.read('xl/workbook.xml');
   for n in ('Dashboard','Monthly','Store','Product','Tax','Clean_Data','Data_Quality','README'): self.assertIn(f'name="{n}"'.encode(),wb)
   worksheets=b''.join(z.read(name) for name in z.namelist() if name.startswith('xl/worksheets/sheet')); self.assertIn(b'Clean_Data!',worksheets); self.assertIn(b'Store!',worksheets); self.assertEqual(len([name for name in z.namelist() if name.startswith('xl/charts/chart')]),2); self.assertNotIn(b'net_sales',b''.join(z.read(name) for name in z.namelist() if name.endswith('.xml')))
 def test_future_case_is_separate(self):
  path=ROOT/'sample_data/future_test/future_food_1pct_2027.csv'; text=path.read_text(encoding='utf-8-sig'); self.assertIn('0.01',text); self.assertIn('2027年4月以降',text); rows=list(csv.DictReader(io.StringIO(text))); self.assertNotIn('',rows[0]); self.assertEqual(rows[0]['tax_category'],'future_food')
 def test_tax_master_is_explicit(self):
  contract=json.loads(CONTRACT.read_text(encoding='utf-8')); self.assertEqual(len(contract['product_tax_master']),24); self.assertEqual({item['rate'] for item in contract['product_tax_master'].values()},{'0.08','0.10'})
 def test_multiple_outputs_are_zipped(self):
  payload=zip_outputs({'a.csv':b'a','b.csv':b'b'}); self.assertEqual(set(zipfile.ZipFile(io.BytesIO(payload)).namelist()),{'a.csv','b.csv'})
if __name__=='__main__': unittest.main()
