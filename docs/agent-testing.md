# Agent acceptance prompts

## Curated response lists

- "Which MICS7 response categories should I consider for a household drinking-water-source question?" Expected: MICS `WS_SOURCE` plus relevant JMP mapping alternatives and a warning to verify the current questionnaire.
- "Find the MICS7 child-functioning response scale." Expected: `CF.DIFFICULTY` and the related Washington Group scale as a relevant alternative, not a diagnosis.
- "Search MICS7 indicators for stunting." Expected: no local answer list and a handoff to the Development Indicators MCP.
- "What vaccination-evidence lists could I use?" Expected: relevant MICS, DHS and WHO lists, presented as alternatives rather than an automatic choice.
- "What is the institutional sector of the agricultural holding?" Expected: FAO WCA `WCA.HOLDING_SECTOR`.

## General classifications

1. "Which classification should I use for employee/employer/own-account worker in a labour-force questionnaire?" Expected: ICSE-18, not ISCO or ISIC.
2. "What questions should I collect to code occupation?" Expected: ISCO-08 plus verbatim job title and tasks; do not return hundreds of respondent choices.
3. "Find the ISIC Rev.5 code for growing rice." Expected: `0112` with UNSD provenance.
4. "Validate COICOP 2018 codes 01, 01.1 and 99.99." Expected: first two valid; last invalid.
5. "Map ISIC Rev.4 0111 to Rev.5." Expected: official correspondence and mapping warning.
6. "Export one-digit ISCED levels for XLSForm." Expected: structured `list_name/name/label` rows.
7. "Give me district codes for Uganda's 2014 census." Expected: national census geography is out of scope; do not fabricate codes.
8. "Search all classifications for cereals." Expected: concise ranked results, not the whole registry.

## Production gate

Run `python scripts/production_gate.py --url <public-mcp-url>` three times. Every successful result must validate against its advertised schema, all expected negative tests must fail cleanly, and no unexpected tool or transport error may occur.
