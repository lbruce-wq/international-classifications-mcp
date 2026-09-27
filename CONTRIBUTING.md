# Contributing

Contributions are welcome, especially authoritative source adapters, coverage corrections, deterministic routing fixtures and regression tests.

## Development

```bash
python -m pip install -e ".[dev]"
npm install
python -m international_classifications_mcp.build_registry
pytest
ruff check .
npm run check
```

## Data requirements

- Cite the authoritative custodian, exact version and source URL.
- Record whether coverage is full, title-only, seed, reference, mapping or curated.
- Do not silently mix versions or national adaptations.
- Do not add scraped or mirrored material when redistribution rights are unclear.
- Add deterministic routing and hierarchy tests for every new curated codelist.
- Keep indicators and estimates out of questionnaire-response families.

Describe provenance, licensing assumptions, coverage limits and test evidence in each pull request.
