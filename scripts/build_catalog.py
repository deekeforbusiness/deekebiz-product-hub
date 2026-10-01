#!/usr/bin/env python3
"""Keep static offers, catalog cards, schema prices and campaign links in sync.

Run from any directory: python scripts/build_catalog.py
No paid product files, analytics credentials, or browser answers belong here.
"""
import html
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://deekeforbusiness.github.io/deekebiz-product-hub/'
CATALOG = json.loads((ROOT / 'products/catalog.json').read_text())
PRODUCTS = CATALOG['products']
BY_PATH = {p['path']: p for p in PRODUCTS}
CAMPAIGN = 'existing_products_2026_10'


def esc(value):
    return html.escape(str(value), quote=True)


def price(p):
    return f"${p['price']}{'+' if p['payWhatYouWant'] else ''} USD"


def buy_url(p, content):
    return p['url'] + '?' + urlencode(dict(utm_source='deekebiz_site', utm_medium='website', utm_campaign=CAMPAIGN, utm_content=content))


def block(text, key, content):
    start, end = f'<!-- generated:{key}:start -->', f'<!-- generated:{key}:end -->'
    replacement = f'{start}\n{content}\n{end}'
    if start in text:
        return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: replacement, text, flags=re.S)
    return text.replace('</main>', replacement + '\n</main>', 1)


def offer(p):
    pricing = 'One-time purchase. You may pay above the stated minimum.' if p['payWhatYouWant'] else 'One-time purchase. No DeekeBiz subscription.'
    extra = ''
    if p['id'] == 'ai-ready-workflow-builder-bundle':
        extra = '<p>Guide ($15 minimum) + workspace ($39 minimum) = $54 separately. The $49 bundle saves $5 at the current minimum prices.</p>'
    if p['id'] == 'overdue-payments-agent-bundle':
        extra = '<p class="db-muted">Notion Custom Agents use Notion credits, billed separately by Notion. <a href="https://www.notion.com/help/custom-agent-pricing">Check current Notion requirements and pricing</a>.</p>'
    contents = ''.join(f'<li>{esc(v)}</li>' for v in p['contents'])
    return f'''<section class="section cp-section"><div class="wrap cp-wrap"><div class="db-offer" data-product="{esc(p['id'])}">
<p class="db-product-meta">{esc(p['format'])}</p><h2>What you receive</h2><ul>{contents}</ul>
<p class="db-price">{price(p)}</p><p>{pricing} Checkout may add applicable taxes.</p>{extra}
<p class="db-muted">{esc(p['requirements'])}</p>
<div class="db-actions"><a class="db-link primary" href="{esc(buy_url(p,p['path']+'_offer'))}">Get {esc(p['name'].split(' — ')[0])} — {price(p)}</a><a class="db-link" href="{BASE}#catalog">Compare all products</a></div>
</div></div></section>'''


def catalog():
    categories = {'Client work': 'client-work', 'Business admin': 'business-admin', 'AI workflows': 'ai-workflows', 'Life admin': 'life-admin', 'Decision kits': 'decision-kits'}
    featured = ['client-delivery-os', 'weekly-reset-tracker', 'claritypack10-pro-bundle']
    covers = {
        '7-day-life-admin-reset': 'life-admin-reset-7-day.webp',
        'ai-operations-architect': 'ai-operations-architect.webp',
        'ai-ready-workflow-builder-os': 'workflow-builder-os.webp',
        'client-delivery-os': 'ChatGPT Image May 21, 2026, 11_44_50 PM (1).png',
        'claritypack10': 'contractor-kit-preview.png',
        'the-recovery-desk': 'recovery-desk.webp',
    }
    cards = []
    ordered = sorted(PRODUCTS, key=lambda p: (featured.index(p['id']) if p['id'] in featured else 3, PRODUCTS.index(p)))
    for p in ordered:
        key = categories[p['category']]
        cover = covers.get(p['path'], p['path'] + '.webp')
        if p['path'] == 'claritypack10':
            visual = f'<figure class="store-product-visual pdf"><img src="{BASE}assets/{cover}" width="990" height="1400" loading="lazy" alt=""><figcaption>Real PDF sample</figcaption></figure>'
        elif (ROOT / 'assets' / cover).is_file():
            width, height = (1672, 941) if p['path'] == 'client-delivery-os' else (1600, 1000)
            visual = f'<figure class="store-product-visual"><img src="{BASE}assets/{esc(cover)}" width="{width}" height="{height}" loading="lazy" alt=""><figcaption>Product cover artwork</figcaption></figure>'
        elif p['id'] == 'overdue-payments-agent-bundle':
            visual = '<figure class="store-product-visual invoice"><div><span>INVOICE FOLLOW-UP</span><strong>One reminder.<br>A clear next step.</strong><small>Draft → Review → Follow up</small></div><figcaption>Illustrative workflow</figcaption></figure>'
        else:
            raise ValueError(f"Missing product artwork for {p['id']}: assets/{cover}")
        title = p['name'].split(' — ')[0]
        cards.append(f'''<article class="db-product" data-product="{esc(p['id'])}" data-category="{key}" data-featured="{'true' if p['id'] in featured else 'false'}"><a class="store-product-link" href="{BASE}{p['path']}/" aria-labelledby="name-{p['id']}">{visual}<div class="store-product-copy"><p class="db-product-meta">{esc(p['format'])}</p><h3 id="name-{p['id']}">{esc(title)}</h3><p>{esc(p['summary'])}</p><div class="store-product-footer"><p class="db-price">{price(p)}</p><span>See contents <span aria-hidden="true">↗</span></span></div></div></a></article>''')
    filters = ['<a href="#featured" class="store-filter" data-category-link="featured" aria-controls="product-grid">Start here</a>', '<a href="#catalog" class="store-filter" data-category-link="all" aria-controls="product-grid">All 16</a>']
    for label, key in categories.items():
        count = sum(p['category'] == label for p in PRODUCTS)
        filters.append(f'<a href="#catalog-{key}" class="store-filter" data-category-link="{key}" aria-controls="product-grid">{label} <span>{count}</span></a>')
    markers = ''.join(f'<span id="catalog-{key}" class="store-anchor" aria-hidden="true"></span>' for key in categories.values())
    return f'''<section id="catalog" class="section store-catalog"><div class="wrap"><span id="featured" class="store-anchor" aria-hidden="true"></span>{markers}<div class="store-section-heading"><div><span class="kicker">Find your fit</span><h2>One useful system.<br>A clearer next step.</h2></div><p>Start with the problem you have.<br>See the contents before you choose.</p></div><nav class="store-filters" aria-label="Filter products">{''.join(filters)}</nav><p class="store-count" data-product-count role="status" aria-live="polite">16 products · prices in USD</p><div id="product-grid" class="db-products">{''.join(cards)}</div><div class="store-catalog-note"><p>“+” means you may pay more than the listed minimum. All products are one-time purchases; software requirements are listed on each product page.</p><p>Cover images are promotional artwork. The ClarityPack10 preview is a real page from the paid PDF kit.</p></div><noscript><p>All 16 products are shown. Select a product to see its contents and requirements.</p></noscript></div></section>'''


def localize_match(match, page):
    attr, quote, value = match.group(1), match.group(2), html.unescape(match.group(3))
    if value.startswith(BASE):
        parsed = urlsplit(value)
        target = ROOT / parsed.path.removeprefix('/deekebiz-product-hub/')
        rel = os.path.relpath(target, page.parent).replace(os.sep, '/')
        if parsed.path.endswith('/'):
            rel = './' if rel == '.' else rel.rstrip('/') + '/'
        value = urlunsplit(('', '', rel, parsed.query, parsed.fragment))
    parsed = urlsplit(value)
    if not parsed.netloc and parsed.path.endswith(('.css', '.js')):
        asset = (page.parent / unquote(parsed.path)).resolve()
        if asset.is_file() and asset.is_relative_to(ROOT):
            query = dict(parse_qsl(parsed.query))
            query['v'] = hashlib.sha256(asset.read_bytes()).hexdigest()[:10]
            value = urlunsplit(('', '', parsed.path, urlencode(query), parsed.fragment))
    return attr + '=' + quote + esc(value) + quote


def rewrite_link(match, page):
    prefix, value, suffix = match.group(1), html.unescape(match.group(2)), match.group(3)
    parsed = urlsplit(value)
    if parsed.netloc != 'deekebiz.gumroad.com' or not parsed.path.startswith('/l/'):
        return match.group(0)
    query = dict(parse_qsl(parsed.query))
    query.update(utm_source='deekebiz_site', utm_medium='website', utm_campaign=CAMPAIGN)
    query.setdefault('utm_content', page.parent.relative_to(ROOT).as_posix().replace('/', '_').replace('.', 'home'))
    return prefix + esc(urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(query),parsed.fragment))) + suffix


for page in sorted(ROOT.rglob('*.html')):
    text = page.read_text()
    path = page.parent.relative_to(ROOT).as_posix()
    if path in BY_PATH:
        p = BY_PATH[path]
        text = block(text, 'offer', offer(p))
        def schema(match):
            data = json.loads(match.group(1))
            nodes = data.get('@graph', [data])
            for node in nodes:
                if node.get('@type') == 'Product':
                    node['name'] = p['name']
                    node['offers'].update(price=str(p['price']), priceCurrency=p['currency'], url=p['url'])
            return '<script type="application/ld+json">' + json.dumps(data,ensure_ascii=False,separators=(',', ':')) + '</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema, text, flags=re.S)
    if path == '.':
        text = block(text, 'catalog', catalog())
    if 'assets/commerce.css' not in text:
        text = text.replace('</head>', f'<link rel="stylesheet" href="{BASE}assets/commerce.css">\n</head>')
    text = re.sub(r'(href|src)=([\"\'])(.*?)\2', lambda m: localize_match(m,page), text)
    canonical = BASE + ('' if path == '.' else path + '/')
    text = re.sub(r'(<link\b[^>]*rel="canonical"[^>]*href=")(.*?)(")', lambda m: m.group(1) + canonical + m.group(3), text)
    text = re.sub(r'(<a\b[^>]*\bhref=")(.*?)(")', lambda m: rewrite_link(m,page), text)
    if path == 'weekly-reset-tracker':
        text = text.replace('3–5', '1–3').replace('3-5', '1–3')
    page.write_text(text)

print(f'Updated {len(PRODUCTS)} static offers, homepage catalog, local assets, and Gumroad campaign links.')
