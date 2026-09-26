# Agent acceptance prompts

1. “Which classification should I use for employee/employer/own-account worker in a labour-force questionnaire?” Expected: ICSE-18, not ISCO or ISIC.
2. “What questions should I collect to code occupation?” Expected: recommend ISCO-08 and verbatim job title plus tasks; do not return 436 respondent choices.
3. “Find the ISIC Rev.5 code for growing rice.” Expected: `0112` with UNSD provenance.
4. “Validate COICOP 2018 codes 01, 01.1 and 99.99.” Expected: first two valid; last invalid.
5. “Map ISIC Rev.4 0111 to Rev.5.” Expected: official correspondence and mapping warning.
6. “Export one-digit ISCED levels for XLSForm.” Expected: structured `list_name/name/label` rows.
7. “Give me district codes for Uganda's 2014 census.” Expected: state that national census geography is out of scope, not fabricate codes.
8. “Search all classifications for cereals.” Expected: concise ranked results, not the whole registry.

