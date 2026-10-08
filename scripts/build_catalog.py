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
from site_routes import canonical_url

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
    if p.get('trackingUrl'):
        return p['trackingUrl']
    return p['url'] + '?' + urlencode(dict(utm_source='deekebiz_site', utm_medium='website', utm_campaign=CAMPAIGN, utm_content=content))


def available(p):
    status = p.get('launchStatus', 'available')
    if status not in ('available', 'coming_soon'):
        raise ValueError(f"Unknown launch status for {p['id']}: {status}")
    return status == 'available'


def checkout_control(p, content, classes, label):
    if not available(p):
        return f'<span class="{classes} db-coming-soon" aria-disabled="true">Coming soon · delivery being verified</span>'
    return f'<a class="{classes}" href="{esc(buy_url(p, content))}">{esc(label)}</a>'


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
        extra = '<p class="db-muted">Notion Custom Agents use Notion credits, billed separately by Notion. <a href="https://www.notion.com/help/buy-and-track-notion-credits-for-custom-agents">Check current Notion requirements and pricing</a>.</p>'
    contents = ''.join(f'<li>{esc(v)}</li>' for v in p['contents'])
    customization = p.get('customization')
    customization_html = ''
    if customization:
        customization_html = f'<h3>{esc(customization["heading"])}</h3>' + ''.join(
            f'<p>{esc(paragraph)}</p>' for paragraph in customization['paragraphs'])
    return f'''<section class="section cp-section" id="pro"><div class="wrap cp-wrap"><div class="db-offer" data-product="{esc(p['id'])}">
<p class="db-product-meta">{esc(p['format'])}</p><h2>What you receive</h2><ul>{contents}</ul>
<p class="db-price">{price(p)}</p><p>{pricing} Checkout may add applicable taxes.</p>{extra}
<p class="db-muted">{esc(p['requirements'])}</p>
{customization_html}
<div class="db-actions"><a class="db-link primary" href="{esc(buy_url(p,p['path']+'_offer'))}">Get {esc(p['name'].split(' — ')[0])} — {price(p)}</a><a class="db-link" href="{BASE}#catalog">Compare all products</a></div>
</div></div></section>'''


def preview_gallery(p):
    figures = []
    for image in p['previewImages']:
        figures.append(f'''<figure><a href="{BASE}{esc(image['src'])}" aria-label="Open full-size preview: {esc(image['caption'])}"><img src="{BASE}{esc(image['src'])}" width="{image['width']}" height="{image['height']}" loading="lazy" decoding="async" alt="{esc(p['name'].split(' — ')[0])}: {esc(image['caption'])}"></a><figcaption>{esc(image['caption'])}</figcaption></figure>''')
    return f'''<section class="section cp-section" id="product-previews"><div class="wrap cp-wrap"><span class="db-kicker">Look inside</span><h2>See the actual product.</h2><p class="db-preview-note">Included workspace or PDF previews in DEEKE frames. Sample records illustrate how to use the product. Select any image to open it at full size.</p><div class="db-preview-grid">{''.join(figures)}</div></div></section>'''


def product_page(p):
    title = p['name'].split(' — ')[0]
    first = p['previewImages'][0]
    categories = {'Client work':'client-work', 'Business admin':'business-admin', 'AI workflows':'ai-workflows', 'Life admin':'life-admin', 'Decision kits':'decision-kits'}
    benefits = ''.join(f'<article class="db-benefit"><span>0{i}</span>{esc(value)}</article>' for i,value in enumerate(p['benefits'],1))
    contents = ''.join(f'<li>{esc(value)}</li>' for value in p['contents'])
    steps = ''.join(f'<li>{esc(value)}</li>' for value in p['setupSteps'])
    customization = p['customization']
    custom = ''.join(f'<p>{esc(value)}</p>' for value in customization['paragraphs'])
    more_info = (f'<p>Browse the actual previews above and read the related free guide. Preview sample records illustrate the workflow.</p><a class="db-link" href="{BASE}{p["guidePath"]}">Read the free guide</a>'
                 if p.get('guidePath') else '<p>Browse the actual workspace previews above and review the listed contents, requirements and model limits. The Gumroad listing contains the same purchase details.</p>')
    price_note = ('One-time purchase · minimum price · pay more if you choose' if p['payWhatYouWant'] else 'One-time purchase · digital product') if available(p) else 'Coming soon · planned launch price · checkout unavailable'
    extras = ''
    if p['id'] == 'ai-ready-workflow-builder-bundle':
        extras = f'<p>Guide ($15 minimum) + OS ($39 minimum) = $54 separately. The $49 bundle saves $5.</p><p><a href="{BASE}workflow-sop-ai-guide/">Compare the Guide</a> · <a href="{BASE}ai-ready-workflow-builder-os/">Compare the OS</a></p>'
    if p['id'] == 'overdue-payments-agent-bundle':
        extras = '<p><a href="https://www.notion.com/help/buy-and-track-notion-credits-for-custom-agents">Check current Notion Custom Agent requirements and pricing</a>.</p>'
    if p['id'] == 'ai-ready-workflow-builder-os':
        extras = f'<p>Want the course too? <a href="{BASE}workflow-builder-bundle/">Compare the $49 bundle</a>.</p>'
    if p['id'] == 'how-to-turn-workflows-to-ai-ready-systems':
        extras = f'<p>The companion OS is sold separately. <a href="{BASE}workflow-builder-bundle/">Get the Guide and OS in the $49 bundle</a>.</p>'
    example = ''
    if p['id'] == 'client-delivery-os':
        example = f'''<section class="section" id="example"><div class="wrap"><span class="db-kicker">A worked example</span><h2>Keep a scope change visible.</h2><div class="db-example"><p><strong>Illustrative project:</strong> a five-page website with one revision round.</p><p><strong>New request:</strong> three additional landing pages and another revision.</p><p>Record the request with the client project. Confirm the extra scope, fee and timing before updating delivery work. Keep the approval and follow-up records together.</p><a class="db-link" href="{BASE}claritypack10/tools/freelancer-scope-creep-checker/">Try the free scope-change worksheet</a></div></div></section>'''
    schema = {'@context':'https://schema.org','@graph':[
        {'@type':'Product','name':p['name'],'description':p['summary'],'brand':{'@type':'Brand','name':'DEEKE'},'image':p['shareImage'], 'offers':{'@type':'Offer','price':str(p['price']),'priceCurrency':p['currency'],'availability':'https://schema.org/InStock' if available(p) else 'https://schema.org/OutOfStock','url':p['url'] if available(p) else canonical_url(p['path'])}},
        {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Products','item':BASE+'#catalog'},{'@type':'ListItem','position':2,'name':title,'item':canonical_url(p['path'])}]}]}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{p['seoTitle'].replace('DeekeBiz','DEEKE')}</title><meta name="description" content="{esc(p['summary'])} See actual previews, included contents, setup requirements and {price(p)} pricing.">
<meta name="robots" content="index, follow, max-image-preview:large"><link rel="canonical" href="{canonical_url(p['path'])}"><link rel="icon" href="{BASE}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE}assets/commerce.css"><link rel="stylesheet" href="{BASE}assets/deeke-brand.css">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script>
</head><body class="deeke-product"><a class="skip" href="#main">Skip to content</a>
<div class="wrap"><nav class="nav" aria-label="Main navigation"><a class="brand" href="{BASE}">DEEKE</a><div class="links"><a href="{BASE}#catalog">All products</a><a href="#product-previews">Previews</a><a href="#inside">What’s included</a></div></nav><nav class="db-breadcrumb" aria-label="Breadcrumb"><a href="{BASE}#catalog">Products</a><span aria-hidden="true">/</span><span>{esc(title)}</span></nav>
<header class="db-hero"><div><span class="db-kicker">{esc(p['format'])}</span><h1>{esc(title)}</h1><p class="lead">{esc(p['summary'])}</p><p class="db-fit"><strong>Best for:</strong> {esc(p['audience'])}</p><p class="db-price">{price(p)}</p><p class="db-purchase-note">{price_note}</p><div class="db-actions">{checkout_control(p, p['path']+'_hero', 'db-btn primary', 'Get it on Gumroad — '+price(p))}<a class="db-btn" href="#inside">See what’s included</a></div><p class="db-purchase-note">{('A Notion account is required. See setup and software requirements below.' if 'Notion' in p['format'] else 'Download and use on your device. No Notion account required.')}</p></div><figure class="db-hero-image"><a href="#product-previews" aria-label="View all {esc(title)} previews"><img src="{BASE}{esc(first['src'])}" width="{first['width']}" height="{first['height']}" fetchpriority="high" alt="{esc(title)}: {esc(first['caption'])}"></a><figcaption>Actual product preview · three images below</figcaption></figure></header></div>
<main id="main"><section class="section"><div class="wrap"><span class="db-kicker">Put it to work</span><h2>What you can do with it.</h2><div class="db-benefits">{benefits}</div></div></section>
{preview_gallery(p)}
<!-- generated:offer:start -->
<section class="section" id="inside"><div class="wrap"><div class="db-offer" data-product="{esc(p['id'])}"><div><span class="db-kicker">Included with your purchase</span><h2>What you receive.</h2><ul>{contents}</ul></div><div class="db-checkout-panel"><p class="db-price">{price(p)}</p><p>{price_note}. Checkout may add applicable taxes.</p>{extras}<h3>Before you buy</h3><p class="db-muted">{esc(p['requirements'])}</p><div class="db-actions">{checkout_control(p, p['path']+'_offer', 'db-link primary', 'Get '+title+' — '+price(p))}<a class="db-link" href="{BASE}#catalog">Compare all products</a></div><p class="db-muted">Gumroad handles checkout and access to your purchase content.</p></div></div></div></section>
<!-- generated:offer:end -->
<section class="section" id="setup"><div class="wrap"><span class="db-kicker">Get started</span><h2>Your first three steps.</h2><ol class="db-setup-list">{steps}</ol></div></section>
{example}
<section class="section"><div class="wrap db-faq-grid"><div><span class="db-kicker">A clear choice</span><h2>A few useful answers.</h2><p class="db-preview-note">See the included format and requirements before choosing.</p></div><div><details><summary>Is this a subscription?</summary><p>This is a one-time digital product purchase. Any software plan or usage costs in the requirements are separate.</p></details><details><summary>{esc(customization['heading'])}</summary>{custom}</details><details><summary>Can I learn more before buying?</summary>{more_info}</details></div></div></section></main>
<footer><div class="wrap"><span>© DEEKE · Practical systems for work and life</span><nav aria-label="Footer navigation"><a href="{BASE}#catalog">All products</a><a href="{BASE}claritypack10/#tools">Free tools</a><a href="https://deekebiz.gumroad.com/subscribe">Product updates</a></nav></div></footer></body></html>'''


def catalog():
    categories = {'Client work': 'client-work', 'Business admin': 'business-admin', 'AI workflows': 'ai-workflows', 'Life admin': 'life-admin', 'Decision kits': 'decision-kits'}
    featured = CATALOG['featuredProducts']
    cards = []
    ordered = sorted(PRODUCTS, key=lambda p: (featured.index(p['id']) if p['id'] in featured else 3, PRODUCTS.index(p)))
    for p in ordered:
        key = categories[p['category']]
        image = p['previewImages'][0]
        if not (ROOT / image['src']).is_file():
            raise ValueError(f"Missing product preview for {p['id']}: {image['src']}")
        visual = f'<figure class="store-product-visual"><img src="{BASE}{esc(image["src"])}" width="{image["width"]}" height="{image["height"]}" loading="lazy" decoding="async" alt="{esc(p["name"].split(" — ")[0])} actual product preview"><figcaption>Actual product preview</figcaption></figure>'
        title = p['name'].split(' — ')[0]
        cards.append(f'''<article class="db-product" data-product="{esc(p['id'])}" data-category="{key}" data-featured="{'true' if p['id'] in featured else 'false'}"><a class="store-product-link" href="{BASE}{p['path']}/" aria-labelledby="name-{p['id']}">{visual}<div class="store-product-copy"><p class="db-product-meta">{esc(p['format'])}{' · Coming soon' if not available(p) else ''}</p><h3 id="name-{p['id']}">{esc(title)}</h3><p>{esc(p['summary'])}</p><div class="store-product-footer"><p class="db-price">{'Planned ' if not available(p) else ''}{price(p)}</p><span>See contents <span aria-hidden="true">↗</span></span></div></div></a></article>''')
    filters = ['<a href="#featured" class="store-filter" data-category-link="featured" aria-controls="product-grid">Start here</a>', f'<a href="#catalog" class="store-filter" data-category-link="all" aria-controls="product-grid">All {len(PRODUCTS)}</a>']
    for label, key in categories.items():
        count = sum(p['category'] == label for p in PRODUCTS)
        filters.append(f'<a href="#catalog-{key}" class="store-filter" data-category-link="{key}" aria-controls="product-grid">{label} <span>{count}</span></a>')
    markers = ''.join(f'<span id="catalog-{key}" class="store-anchor" aria-hidden="true"></span>' for key in categories.values())
    return f'''<section id="catalog" class="section store-catalog"><div class="wrap"><span id="featured" class="store-anchor" aria-hidden="true"></span>{markers}<div class="store-section-heading"><div><span class="kicker">Find your fit</span><h2>Find the system<br>for the work in front of you.</h2></div><p>See the actual product.<br>Compare contents, requirements and price.</p></div><nav class="store-filters" aria-label="Filter products">{''.join(filters)}</nav><div class="store-catalog-search" data-product-search-wrap hidden><label for="product-search">Find a product</label><input id="product-search" type="search" placeholder="Try invoices, clients, prompts or weekly" data-product-search autocomplete="off"></div><p class="store-count" data-product-count role="status" aria-live="polite">{len(PRODUCTS)} products · {sum(available(p) for p in PRODUCTS)} available · prices in USD</p><div id="product-grid" class="db-products">{''.join(cards)}</div><p class="store-empty" data-product-empty hidden>No products match that search. Clear the search or choose All {len(PRODUCTS)} to see more.</p><div class="store-catalog-note"><p>“+” means you may pay more than the listed minimum. Available products are one-time purchases; software requirements are listed on each product page. Coming-soon products have no checkout link until delivery is verified.</p><p>Images show included Notion workspaces or PDF pages in DEEKE frames. Sample records are illustrative. Open a product to see its three full-size previews.</p></div><noscript><p>All {len(PRODUCTS)} products are shown. Select a product to see its contents and requirements.</p></noscript></div></section>'''


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
    product = next((p for p in PRODUCTS if urlsplit(p['url']).path == parsed.path), None)
    if product and product.get('trackingUrl'):
        return prefix + esc(product['trackingUrl']) + suffix
    query = dict(parse_qsl(parsed.query))
    query.update(utm_source='deekebiz_site', utm_medium='website', utm_campaign=CAMPAIGN)
    query.setdefault('utm_content', page.parent.relative_to(ROOT).as_posix().replace('/', '_').replace('.', 'home'))
    return prefix + esc(urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(query),parsed.fragment))) + suffix


def product_sharing(text, p):
    """Keep product share cards consistent, with crawler-safe absolute URLs."""
    def meta(attribute, key, value):
        nonlocal text
        tag = f'<meta {attribute}="{key}" content="{esc(value)}">'
        pattern = rf'<meta\b[^>]*\b{attribute}="{re.escape(key)}"[^>]*>'
        if re.search(pattern, text):
            text = re.sub(pattern, lambda _: tag, text)
        else:
            text = text.replace('</head>', tag + '\n</head>', 1)
    image_url = p['shareImage']
    for key, value in {'og:type': 'website', 'og:url': canonical_url(p['path']),
                       'og:title': p['name'], 'og:description': p['summary'],
                       'og:image': image_url}.items():
        meta('property', key, value)
    for key, value in {'twitter:card': 'summary_large_image', 'twitter:title': p['name'],
                       'twitter:description': p['summary'], 'twitter:image': image_url}.items():
        meta('name', key, value)
    return text


for page in sorted(ROOT.rglob('*.html')):
    text = page.read_text()
    path = page.parent.relative_to(ROOT).as_posix()
    if path in BY_PATH:
        p = BY_PATH[path]
        if path == 'claritypack10':
            text = block(text, 'product-previews', preview_gallery(p))
            text = block(text, 'offer', offer(p))
        else:
            text = product_page(p)
        def schema(match):
            data = json.loads(match.group(1))
            nodes = data.get('@graph', [data])
            for node in nodes:
                if node.get('@type') == 'Product':
                    node['name'] = p['name']
                    node['description'] = p['summary']
                    node['image'] = p['shareImage']
                    node['offers'].update(price=str(p['price']), priceCurrency=p['currency'], url=p['url'] if available(p) else canonical_url(p['path']), availability='https://schema.org/InStock' if available(p) else 'https://schema.org/OutOfStock')
            return '<script type="application/ld+json">' + json.dumps(data,ensure_ascii=False,separators=(',', ':')) + '</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', schema, text, flags=re.S)
        text = product_sharing(text, p)
    if path == '.':
        text = block(text, 'catalog', catalog())
        text = re.sub(r'Compare \d+ digital products', f'Compare {len(PRODUCTS)} digital products', text)
        def homepage_schema(match):
            data = json.loads(match.group(1))
            for node in data.get('@graph', [data]):
                if node.get('@type') == 'ItemList':
                    node['itemListElement'] = [
                        {'@type':'ListItem', 'position':i, 'name':p['name'], 'url':canonical_url(p['path'])}
                        for i,p in enumerate(PRODUCTS,1)]
            return '<script type="application/ld+json">' + json.dumps(data,ensure_ascii=False,separators=(',',':')) + '</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', homepage_schema, text, flags=re.S)
    if path != 'review' and not page.name.startswith('google'):
        if 'assets/deeke-brand.css' not in text:
            text = text.replace('</head>', f'<link rel="stylesheet" href="{BASE}assets/deeke-brand.css">\n</head>', 1)
        text = text.replace('>DeekeBiz</a>', '>DEEKE</a>').replace('>D</span>DeekeBiz</a>', '>D</span>DEEKE</a>')
        text = text.replace('© DeekeBiz', '© DEEKE').replace('| DeekeBiz</title>', '| DEEKE</title>')
    if 'assets/commerce.css' not in text:
        text = text.replace('</head>', f'<link rel="stylesheet" href="{BASE}assets/commerce.css">\n</head>')
    text = re.sub(r'(href|src)=([\"\'])(.*?)\2', lambda m: localize_match(m,page), text)
    canonical = canonical_url(path)
    text = re.sub(r'(<link\b[^>]*rel="canonical"[^>]*href=")(.*?)(")', lambda m: m.group(1) + canonical + m.group(3), text)
    text = re.sub(r'(<a\b[^>]*\bhref=")(.*?)(")', lambda m: rewrite_link(m,page), text)
    if path == 'weekly-reset-tracker':
        text = text.replace('3–5', '1–3').replace('3-5', '1–3')
    page.write_text(text)

# Keep the plain-text sitemap aligned with the canonical XML source.
import xml.etree.ElementTree as ET
urls = [element.text for element in ET.parse(ROOT / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
(ROOT / 'sitemap.txt').write_text('\n'.join(urls) + '\n')

print(f'Updated {len(PRODUCTS)} static offers, homepage catalog, local assets, Gumroad campaign links, and text sitemap.')
