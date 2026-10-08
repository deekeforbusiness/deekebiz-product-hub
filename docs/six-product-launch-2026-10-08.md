# Six-product catalog expansion

Six self-contained Notion products have dedicated catalog pages, confirmed launch prices, three real workspace previews each, and setup and software requirements. The catalog uses the existing DEEKE branding and category filters.

| Product | Price | Catalog category | Launch state |
| --- | --- | --- | --- |
| Creative Asset License Vault | $15 | Business admin | Available on Gumroad |
| Pet Sitter Visit Desk | $19 | Client work | Available on Gumroad |
| New Hire Training Desk | $19 | Business admin | Available on Gumroad |
| Etsy Digital Seller Desk | $19 | Business admin | Coming soon; public buyer delivery pending |
| Stock & Reorder Desk | $19 | Business admin | Coming soon; public buyer delivery pending |
| Tenant Turnover Evidence Kit | $19 | Life admin | Coming soon; public buyer delivery and Gumroad artwork pending |

The coming-soon state removes checkout links and marks structured-data availability as OutOfStock. Change `launchStatus` to `available` only after the public duplication route and the Gumroad purchase-content link are verified. Regenerate with `python scripts/build_catalog.py` and validate with `python scripts/check_site.py`.

The website contains marketing previews, not the paid Notion access links or buyer copies. Template samples are fictional. These products support manual recordkeeping and review; no sending, purchasing, platform synchronization, certification, legal determination or automated inspection is included.

Checks passed: 64 pages, 1,128 internal links/assets/anchors, 60 canonical sitemap URLs, 23 catalog entries, and 15 existing JavaScript tests. The new launch-state check prevents a coming-soon product from exposing its Gumroad checkout link. Live browser checks follow deployment.

Seller, Stock and Tenant masters remain separate roots in Main Hub because Notion workspace creation failed. Their existing private copy tests do not substitute for the remaining public buyer-copy tests.
