#!/usr/bin/env python3
"""Check static deployment routes, anchors, structured data and public catalog."""
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from site_routes import canonical_url, REDIRECTS

ROOT=Path(__file__).resolve().parents[1]
BASE='https://deekeforbusiness.github.io/deekebiz-product-hub/'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.links=[];self.assets=[];self.schemas=[];self.canonical=[];self.meta={};self.featured=[];self.robots='';self.refresh=[];self.h1=0;self.in_schema=False;self.schema='';self.feed(text)
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if a.get('id'):self.ids.append(a['id'])
        if a.get('data-featured')=='true':self.featured.append(a['data-product'])
        if tag=='meta':self.meta[a.get('property',a.get('name',''))]=a.get('content','')
        if tag=='h1':self.h1+=1
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag in ['img','script'] and a.get('src'):self.assets.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.assets.append(a['href'])
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='meta' and a.get('name','').lower()=='robots':self.robots=a.get('content','').lower()
        if tag=='meta' and a.get('http-equiv','').lower()=='refresh':self.refresh.append(a.get('content',''))
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
    if page.canonical!=[canonical_url(relative)]:errors.append(f'{relative}: incorrect canonical {page.canonical}')
    if relative in REDIRECTS:
        if page.refresh!=['0; url='+BASE+REDIRECTS[relative]]:errors.append(f'{relative}: incorrect permanent meta redirect')
        if 'noindex' in page.robots:errors.append(f'{relative}: noindex conflicts with guide consolidation')
    elif page.refresh:errors.append(f'{relative}: unregistered redirect')
    for target in page.links+page.assets:
        u=urlsplit(urljoin(url,target))
        if u.netloc!='deekeforbusiness.github.io':continue
        if not u.path.startswith('/deekebiz-product-hub/'):continue
        local=ROOT/unquote(u.path[len('/deekebiz-product-hub/'):]);local=local/'index.html' if u.path.endswith('/') else local
        checked+=1
        if not local.is_file():errors.append(f'{relative}: missing route/asset {target}')
        elif u.fragment and local in pages and unquote(u.fragment) not in pages[local].ids:errors.append(f'{relative}: missing anchor {target}')
        if local in pages and local.parent.relative_to(ROOT).as_posix() in REDIRECTS:errors.append(f'{relative}: internal link uses legacy redirect {target}')

namespace={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
sitemap=ET.parse(ROOT/'sitemap.xml').getroot()
sitemap_urls=[entry.find('s:loc',namespace).text for entry in sitemap]
expected_urls={canonical_url(path.parent.relative_to(ROOT).as_posix()) for path,page in pages.items()
               if path.name=='index.html' and not page.refresh and 'noindex' not in page.robots}
if len(sitemap_urls)!=len(set(sitemap_urls)):errors.append('sitemap: duplicate URLs')
text_sitemap_urls=(ROOT/'sitemap.txt').read_text().splitlines()
if text_sitemap_urls!=sitemap_urls:errors.append('text sitemap: does not match canonical XML sitemap')
if set(sitemap_urls)!=expected_urls:errors.append(f'sitemap: missing {sorted(expected_urls-set(sitemap_urls))}; unexpected {sorted(set(sitemap_urls)-expected_urls)}')
for entry in sitemap:
    lastmod=entry.findtext('s:lastmod','',namespace)
    if lastmod and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',lastmod):errors.append('sitemap: invalid lastmod date')
catalog_data=json.loads((ROOT/'products/catalog.json').read_text())
catalog=catalog_data['products']
assert len(catalog)==16
if pages[ROOT/'index.html'].featured!=catalog_data['featuredProducts']:errors.append('homepage: featured products do not match catalog configuration')
for p in catalog:
    text=(ROOT/p['path']/'index.html').read_text()
    if text.count('generated:offer:start')!=1:errors.append(f'{p["path"]}: missing/duplicate offer')
    if f'data-product="{p["id"]}"' not in (ROOT/'index.html').read_text():errors.append(f'{p["id"]}: absent from homepage catalog')
    meta=pages[ROOT/p['path']/'index.html'].meta
    if meta.get('og:url')!=canonical_url(p['path']):errors.append(f'{p["id"]}: inconsistent share URL')
    if meta.get('og:title')!=p['name'] or meta.get('twitter:title')!=p['name']:errors.append(f'{p["id"]}: inconsistent share title')
    image=meta.get('og:image','')
    if not image.startswith(BASE) or meta.get('twitter:image')!=image:errors.append(f'{p["id"]}: missing/relative share image')
    elif not (ROOT/unquote(urlsplit(image).path.removeprefix('/deekebiz-product-hub/'))).is_file():errors.append(f'{p["id"]}: missing share image asset')
    nodes=[]
    for data in pages[ROOT/p['path']/'index.html'].schemas:nodes.extend(data.get('@graph',[data]))
    for node in nodes:
        if node.get('@type')=='Product' and (node['offers']['price']!=str(p['price']) or node['offers']['priceCurrency']!=p['currency']):errors.append(f'{p["id"]}: schema price mismatch')
for tool in (ROOT/'claritypack10/tools').glob('*/index.html'):
    text=tool.read_text()
    if 'data-result-upgrade' not in text or 'cp-report-credit' not in text:errors.append(f'{tool.parent.name}: missing contextual result path or attribution')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(pages)-1} pages, {checked} internal links/assets/anchors, {len(sitemap_urls)} canonical sitemap URLs, 3 guide redirects, 16 catalog offers and 10 tool result paths.')
