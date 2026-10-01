# DeekeBiz public catalog

The maintained source is `products/catalog.json`, verified against the public Gumroad catalog on October 1, 2026. It contains all 16 published products, including ClarityPack10 Pro Bundle, with current USD prices, pay-what-you-want status, formats, contents, requirements, and checkout destinations.

Run `python scripts/build_catalog.py` after changing that file. It regenerates the homepage catalog, all product offer blocks, schema prices, and site campaign labels. Existing explanatory copy should also be reviewed when a product changes.

Archived rental analyzers are not in the published catalog and must stay hidden until their live status is verified.
