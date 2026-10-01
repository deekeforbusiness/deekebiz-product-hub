# DeekeBiz product hub

Static HTML website deployed by GitHub Pages from `main`.

`products/catalog.json` maintains the 16 published products. To regenerate their public offer blocks, catalog cards, schema prices, and campaign labels:

```
python scripts/build_catalog.py
python scripts/check_site.py
node --test tests/*.test.cjs
```

See `docs/website-release-2026-10.md` for the current release, browser acceptance limits, and account-dependent measurement work. Paid downloads, credentials, and visitor report data must not be added to this repository.
