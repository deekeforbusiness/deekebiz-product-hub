#!/usr/bin/env python3
"""Check sitemap canonicals and crawlable homepage paths without JavaScript."""
import xml.etree.ElementTree as ET
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://deekeforbusiness.github.io/deekebiz-product-hub/'

class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = set()
        self.canonical = []
        self.robots = ''
        self.refresh = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.links.add(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a.get('href'))
        if tag == 'meta' and a.get('name', '').lower() == 'robots':
            self.robots = a.get('content', '').lower()
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            self.refresh = True

pages = {}
for path in ROOT.rglob('index.html'):
    route = path.parent.relative_to(ROOT).as_posix()
    pages[BASE + ('' if route == '.' else route + '/')] = Links(path.read_text())

def targets(url):
    return {urljoin(url, href).split('#', 1)[0].split('?', 1)[0]
            for href in pages[url].links}

root = ET.parse(ROOT / 'sitemap.xml').getroot()
assert root.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset'
urls = [e.text for e in root.findall('{*}url/{*}loc')]
assert len(urls) == len(set(urls)), 'Duplicate sitemap URLs'
assert urls == (ROOT / 'sitemap.txt').read_text().splitlines()
for url in urls:
    assert url.startswith(BASE) and urlsplit(url).query == '' and urlsplit(url).fragment == '', url
    assert url in pages, f'Missing page: {url}'
    page = pages[url]
    assert page.canonical == [url], f'Non-self-canonical sitemap entry: {url}'
    assert not page.refresh and 'noindex' not in page.robots, url

seen = {BASE}
queue = deque([BASE])
while queue:
    for target in targets(queue.popleft()):
        if target in pages and target not in seen:
            seen.add(target)
            queue.append(target)
assert set(urls) <= seen, f'Orphan sitemap pages: {set(urls) - seen}'
priority = ['workflow-sop-ai-ready-system', 'workflow-sop-checklist',
            'notion-ai-prompt-library', 'ai-operations-workflow-system',
            'brand-activation-production-workflow', 'follow-up-overdue-invoices-politely',
            'weekly-reset-planning-system']
for route in priority:
    url = BASE + 'guides/' + route + '/'
    assert url in targets(BASE), f'Homepage guide link missing: {url}'
    assert url in urls, f'Guide missing from sitemap: {url}'
assert BASE + 'guides/' in targets(BASE)
print(f'PASS: {len(urls)} canonical sitemap pages reachable from homepage; 7 priority guides linked directly in static HTML.')
