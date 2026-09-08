from __future__ import annotations
import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUTPUT=ROOT/'sample_data'/'input'; FUTURE=ROOT/'sample_data'/'future_test'
PRODUCTS=[]
for i in range(1,25):
    cat='reduced' if i<=8 else 'standard'; rate=0.08 if i<=8 else 0.10
    PRODUCTS.append((f'P-{i:03d}', f'Synthetic Product {i:02d}', 800+i*175, cat, rate))
def rows(count,prefix,seed):
    start=date(2025,9,1); result=[]
    for index in range(count):
        sku,product,price,cat,rate=PRODUCTS[(index*7+seed)%len(PRODUCTS)]; q=1+(index+seed)%5
        status='cancelled' if index%41==0 else 'refunded' if index%97==0 else 'completed'
        discount=200 if index%9==0 else 0; shipping=450 if index%4==0 else 0
        # Explicit synthetic product-master rate; tax base is item amount after discount for this demo only.
        tax=round(max(0,q*price-discount)*rate)
        result.append(dict(order_id=f'{prefix}-{index+1:05d}',order_date=start+timedelta(days=(index*11+seed*3)%365),status=status,sku=sku,product=product,quantity=q,price=price,discount=discount,shipping=shipping,tax=tax,tax_category=cat,tax_rate=rate))
    return result
def write_csv(path,fields,rs):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rs)
def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    north,sakura,harbor=rows(340,'N',1),rows(342,'S',2),rows(342,'H',3)
    sakura[-1]=dict(sakura[-2]); harbor[-1]['quantity']='not-a-number'
    sn={'completed':'paid','cancelled':'cancelled','refunded':'refunded'}
    write_csv(OUTPUT/'north_market_2026.csv',['order_no','order_date','status','sku','item','qty','unit_price','discount','shipping','tax'],[{'order_no':r['order_id'],'order_date':r['order_date'].isoformat(),'status':sn[r['status']],'sku':r['sku'],'item':r['product'],'qty':r['quantity'],'unit_price':r['price'],'discount':r['discount'],'shipping':r['shipping'],'tax':r['tax']} for r in north])
    ss={'completed':'発送済','cancelled':'キャンセル','refunded':'返金'}
    write_csv(OUTPUT/'sakura_mall_2026.csv',['注文番号','注文日','状態','商品コード','商品名','個数','販売単価','クーポン','送料','消費税'],[{'注文番号':r['order_id'],'注文日':r['order_date'].strftime('%Y/%m/%d'),'状態':ss[r['status']],'商品コード':r['sku'],'商品名':r['product'],'個数':r['quantity'],'販売単価':r['price'],'クーポン':r['discount'],'送料':r['shipping'],'消費税':r['tax']} for r in sakura])
    sh={'completed':'fulfilled','cancelled':'void','refunded':'refunded'}
    write_csv(OUTPUT/'harbor_shop_2026.csv',['id','created_at','state','product_code','description','units','price_jpy','discount_jpy','delivery_jpy','tax_jpy'],[{'id':r['order_id'],'created_at':datetime.combine(r['order_date'],datetime.min.time(),timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z'),'state':sh[r['status']],'product_code':r['sku'],'description':r['product'],'units':r['quantity'],'price_jpy':r['price'],'discount_jpy':r['discount'],'delivery_jpy':r['shipping'],'tax_jpy':r['tax']} for r in harbor])
    write_csv(FUTURE/'future_food_1pct_2027.csv',['scenario','effective_from','tax_category','tax_rate','sku','quantity','unit_price'],[{'scenario':'2027年4月以降の制度変更を想定したテストケース','effective_from':'2027-04-01','tax_category':'future_food','tax_rate':'0.01','sku':'FUTURE-FOOD-001','quantity':1,'unit_price':1000}])
    print('Generated 1,024 wholly synthetic normal rows plus separate future 1% test case')
if __name__=='__main__': main()
