# Architecture

The service is a deterministic, read-only MCP registry. The connected agent performs natural-language reasoning; this server performs bounded retrieval and never calls an LLM, embedding API or paid AI service.

## Components

1. `catalog.py` defines classification metadata, deterministic concept rules and small operational structures.
2. `build_registry.py` normalizes official source material and curated response lists into the bundled SQLite registry.
3. `registry.py` implements exact lookup, FTS5 search, hierarchy traversal, validation, correspondence mapping, recommendations and exports.
4. `server.py` exposes typed MCP tools and structured schemas.
5. The Cloudflare Worker routes public MCP traffic to a versioned read-only container.

All identifiers are stable within a release. Coverage labels distinguish full structures, title-only structures, seeds, mappings, references and curated questionnaire lists.

## Recommendation contract

Recommendations are deterministic ranked shortlists, not decisions. Relevant alternatives are returned with evidence, role, version and provenance. The caller explicitly chooses a classification and, for curated response families, a `codelist_id` before exporting.

## Curated codelist hierarchy

Root nodes for response-list families use `node_kind: "codelist"`. They are retrievable and valid identifiers. Passing the codelist ID as `parent_code` returns its `node_kind: "code"` options.

## Trust boundary

The SQLite file and bundled rules are the runtime data boundary. Provenance URLs are returned as citations but are not fetched during tool calls, so all tools are read-only, non-destructive and closed-world.
