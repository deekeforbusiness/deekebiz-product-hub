#!/usr/bin/env python3
"""Check static deployment routes, anchors, structured data and public catalog."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
BASE='https://deekeforbusiness.github.io/deekebiz-product-hub/'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.links=[];self.assets=[];self.schemas=[];self.canonical=[];self.h1=0;self.in_schema=False;self.schema='';self.feed(text)
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag in ['img','script'] and a.get('src'):self.assets.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.assets.append(a['href'])
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='script' and a.get('type')=='application/ld+json':self.in_schema=True;self.schema=''
    def handle_data(self,data):
        if self.in_schema:self.schema+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.in_schema:self.schemas.append(json.loads(self.schema));self.in_schema=False

pages={p:Page(p.read_text()) for p in ROOT.rglob('*.html')}
errors=[];checked=0
for path,page in pages.items():
    if path.name.startswith('google'):continue
    relative=path.parent.relative_to(ROOT).as_posix();url=BASE+('' if relative=='.' else relative+'/')
    if len(page.ids)!=len(set(page.ids)):errors.append(f'{relative}: duplicate ids')
    if page.h1!=1:errors.append(f'{relative}: expected one h1')
    if page.canonical!=[url]:errors.append(f'{relative}: incorrect canonical {page.canonical}')
    for target in page.links+page.assets:
        u=urlsplit(urljoin(url,target))
        if u.netloc!='deekeforbusiness.github.io':continue
        if not u.path.startswith('/deekebiz-product-hub/'):continue
        local=ROOT/unquote(u.path[len('/deekebiz-product-hub/'):]);local=local/'index.html' if u.path.endswith('/') else local
        checked+=1
        if not local.is_file():errors.append(f'{relative}: missing route/asset {target}')
        elif u.fragment and local in pages and unquote(u.fragment) not in pages[local].ids:errors.append(f'{relative}: missing anchor {target}')
catalog=json.loads((ROOT/'products/catalog.json').read_text())['products']
assert len(catalog)==16
for p in catalog:
    text=(ROOT/p['path']/'index.html').read_text()
    if text.count('generated:offer:start')!=1:errors.append(f'{p["path"]}: missing/duplicate offer')
    if f'data-product="{p["id"]}"' not in (ROOT/'index.html').read_text():errors.append(f'{p["id"]}: absent from homepage catalog')
    nodes=[]
    for data in pages[ROOT/p['path']/'index.html'].schemas:nodes.extend(data.get('@graph',[data]))
    for node in nodes:
        if node.get('@type')=='Product' and (node['offers']['price']!=str(p['price']) or node['offers']['priceCurrency']!=p['currency']):errors.append(f'{p["id"]}: schema price mismatch')
for tool in (ROOT/'claritypack10/tools').glob('*/index.html'):
    text=tool.read_text()
    if 'data-result-upgrade' not in text or 'cp-report-credit' not in text:errors.append(f'{tool.parent.name}: missing contextual result path or attribution')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(pages)-1} pages, {checked} internal links/assets/anchors, 16 catalog offers and 10 tool result paths.')
