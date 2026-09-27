# International Classifications MCP

A free, open-source, deterministic MCP server for discovering, explaining, validating and mapping official international statistical classifications.

It is designed for questionnaire development, survey coding, statistical harmonisation and reproducible analysis. No LLM, embedding service or paid AI runs inside the server. The connected AI client interprets the user's task; this service provides versioned official structures, deterministic retrieval and provenance.

## Coverage (v0.5.2)

Production safeguards include first-class typed codelist hierarchy nodes, deterministic routing fixtures for every curated codelist, weekly authoritative-link checks, per-tool request IDs and latency logging, and documented OpenAI directory annotation justifications.

The registry includes full machine-readable structures for ISIC Rev.5, CPC 3.0, COICOP 2018, HS 2022, SITC Rev.4, BEC Rev.5 and UN M49; a complete ISCO-08 code/title hierarchy; the official ISIC Rev.4 to Rev.5 correspondence; operational ICSE-18, ICSaW-18 and ISCED structures; detailed ISCED-F and ICCS structures; and clearly labelled reference-only entries for ICD-11 and ICF.

MICS7 is represented only by curated, question-specific response codelists for matching questionnaire answer categories. MICS modules and analytical indicator definitions are intentionally not exposed as classifications; indicator discovery belongs in a development-indicators service. The response layer does not replace UNICEF's current questionnaires or country customisation guidance and never silently combines MICS rounds.

Version 0.5 adds ICC 1.1, ICATUS 2016, COFOG, COPNI, COPP, UNECE Recommendation 20 units and Recommendation 21 package types; detailed ISCED-F and ICCS titles; expanded ICSE/ICSaW and SDMX cores; and separately versioned DHS-8, Washington Group, JMP WASH, WHO vaccination and FAO WCA questionnaire codelists.

Each curated answer list has a stable `codelist_id`. Call `list_codelists`, then pass one identifier to search or export. The server refuses to merge unrelated MICS choices into one questionnaire list.

National census and administrative geography codes are intentionally out of scope because they change frequently and lack one authoritative global registry.

Coverage is explicit in `list_classifications`: `full`, `seed`, `mapping`, `reference`, or `curated`. Reference-only and curated families are never presented as complete code lists.

## Tools

- `list_classifications`
- `get_classification`
- `list_codelists`
- `recommend_classifications`
- `search_codes`
- `get_code_definition`
- `browse_hierarchy`
- `validate_codes`
- `map_codes`
- `export_choice_list`

## Connect

```bash
codex mcp add international-classifications --url https://classifications.impactengines.ai/mcp
```

The root URL provides service status; `/mcp` is the MCP endpoint.

## Local development

```bash
python -m pip install -e ".[dev]"
python -m international_classifications_mcp.build_registry
pytest
classifications-mcp
```

For HTTP transport:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 classifications-mcp
```

## Build philosophy

- Official custodians remain authoritative.
- Source files are hashed and registry releases are versioned.
- Search is programmatic: FTS5, curated concept rules and explicit scoring.
- Correspondences preserve one-to-many and changed-definition warnings.
- Detailed occupations, industries, diseases and crimes are normally post-coded, not dumped into respondent-facing questionnaires.
- Source content remains subject to its custodian's terms; the MIT licence covers this software, not third-party classification content.

See [source audit](docs/source-audit.md) and [agent test prompts](docs/agent-testing.md).

## Documentation

- [Architecture](docs/architecture.md)
- [Source and coverage audit](docs/source-audit.md)
- [Deployment](docs/deployment.md)
- [Production operations](docs/operations.md)
- [OpenAI directory submission evidence](docs/openai-directory-submission.md)
- [Contributing](CONTRIBUTING.md) and [security policy](SECURITY.md)
