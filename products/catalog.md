# Product catalog

The maintained source is `products/catalog.json`, verified against Gumroad on October 8, 2026. All 26 products are published at fixed USD prices. Quick, Core and Pro are listed in the Rental analyzers category at $9, $19 and $49.

The catalog supplies contents, requirements, purchase destinations, actual previews, availability and search/share metadata. Edit it, run `python scripts/build_catalog.py`, then `python scripts/check_site.py` and `node --test tests/*.test.cjs` before deploying. Never commit paid delivery files or private template access links.
