# Website repair and first-sales test

## Published behavior

The hub now exposes all 16 published products with current USD prices and formats. Featured, Catalog, Guides, and Systems anchors resolve. Client Delivery OS has visible $19+ pricing, confirmed workspace contents, a worked project example, setup steps, and a route to the free scope-change tool.

All ten ClarityPack10 reports link to the relevant kit. The complete $19 bundle is distinguished from the free browser report and from the separate $19+ Client Delivery OS. A genuine contractor-kit checklist page is the only paid page used as a public sample. The source ZIP includes ten eight-page PDF kits, a seven-page start guide, and an editable Word script document; the full paid files are not in this repository.

The contractor tool compares integer-cent costs, entered tax, exclusions, scope, and itemized allowances. Missing costs remain unknown. Different or unconfirmed scope prevents ranking. Allowance gaps are separate so they are not automatically counted twice. Existing text drafts are preserved as earlier notes.

Local draft failures display an honest message. Editing invalidates the previous output. Clearing cancels pending autosave. Report attribution includes a public tool URL without answers.

## Validation

Run:

```
python scripts/build_catalog.py
python scripts/check_site.py
node --test tests/*.test.cjs
node --check assets/claritypack.js
node --check assets/quote-comparison.js
```

Static validation covers 56 pages, internal routes/assets/anchors, schema syntax and catalog prices. The calculation tests cover cents, excluded/included tax, unresolved costs, scope, allowances, equality, currency, and HTML injection. The catalog build is repeatable.

Browser acceptance is performed on the existing public GitHub Pages deployment. A local preview was denied by browser access controls. This is not a cross-browser certification or a real checkout/payment test.

## Measurement and remaining account work

- Outbound Gumroad product links carry `utm_source=deekebiz_site`, `utm_medium=website`, `utm_campaign=existing_products_2026_10`, plus placement labels. They never contain tool answers.
- UTM labels alone do not create a site analytics collector. No aggregate visits, completions, or purchases are available from this repository.
- With Gumroad account access, create tracked links under Analytics → Links for the campaign, and install the exact website view snippet supplied by Widgets → Analytics on commercial pages. Preserve the no-report-transmission promise of the browser tools.
- Current sales and traffic must be read from the account. Do not infer sales from ratings or manufacture testimonial/revenue claims.
- Check that the live Gumroad ZIP is the reviewed bundle version, and test delivery of the live Client Delivery OS duplication access. The available product descriptions and local paid kit do not prove checkout delivery.
- Replace promotional artwork with real workspace screenshots when actual Client Delivery OS access is available. Keep the illustrative example clearly labeled.
- In the Gumroad Recovery Desk description, remove the literal editing label “Closing line:” and separate the concatenated final sentences.

## First test

Keep current prices steady. Direct the next relevant client-work content to the free scope-change tool or the Client Delivery OS page. Use one campaign and record the dates, qualified traffic, product visits, checkout clicks, and purchases available from the connected account. Diagnose the observed bottleneck before producing another product or changing all prices. Do not call the site changes a sales result until actual purchases exist.

## Maintaining the catalog

Update `products/catalog.json`, regenerate with `scripts/build_catalog.py`, and run the checks before publishing. Review explanatory copy too when contents, requirements, names, or prices change. No archived rental analyzers are published in the catalog.

## Visual storefront update

The homepage now opens with concise copy and three selectable, clearly labeled illustrative workflows. Five situation cards lead into a filterable visual product collection. The default selection offers Client Delivery OS, Weekly Reset Tracker, and ClarityPack10 as starting points; “All 16” and five category filters expose the full catalog. Direct links to `#catalog` show every product. Category selections have shareable anchors and follow browser back/forward navigation.

Catalog prices and formats are still generated from the canonical catalog. Existing cover artwork is labeled as artwork, and the ClarityPack10 preview is the actual contractor checklist page. The homepage shows that PDF sample at full page proportions and links to its full-size image. The lengthy repeated AI sections are replaced by shorter free-tool, guide, setup, and FAQ sections. Existing `#featured`, `#guides`, `#systems`, and `#catalog` anchors continue to resolve.

The homepage has its own CSS and progressive enhancement script. Without JavaScript, all sixteen products remain available, ordinary anchors work, and the first illustrative workflow remains visible. No analytics collector or transmission of tool answers was added. Prices were not changed.
