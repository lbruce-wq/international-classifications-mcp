# OpenAI directory annotation justifications

All ten tools use the standard MCP `ToolAnnotations` fields. The official OpenAI tool-planning guidance defines these hints but does not define additional justification properties in the MCP schema. The explanations below are therefore maintained as submission evidence for the directory review form rather than emitted as non-standard annotation fields.

Official guidance: https://developers.openai.com/plugins/plan/tools#plan-safety-annotations

| Tool | `readOnlyHint: true` justification | `destructiveHint: false` justification | `openWorldHint: false` justification |
|---|---|---|---|
| `list_classifications` | Reads bundled catalogue metadata only. | Cannot create, update or delete state. | Reads the bounded local registry; returned URLs are provenance strings and are not fetched. |
| `get_classification` | Reads one bundled metadata record. | Cannot modify any record or external system. | Uses an exact local identifier only. |
| `list_codelists` | Reads bundled codelist metadata and counts. | Cannot change codelists. | Does not contact questionnaire custodians or the public internet. |
| `recommend_classifications` | Computes deterministic scores over bundled rules and metadata. | Produces recommendations only and performs no action. | No model call, web search or external lookup occurs. |
| `search_codes` | Searches the bundled SQLite FTS index. | Cannot change codes or index contents. | Search scope is the finite local registry. |
| `get_code_definition` | Reads one bundled code or codelist container. | Cannot modify source data. | Exact lookup remains inside the local registry. |
| `browse_hierarchy` | Reads local parent/child relationships. | Cannot alter hierarchy state. | Traversal is limited to bundled classifications. |
| `validate_codes` | Compares supplied values with local records. | Does not recode or persist user data. | Validation does not query external authorities. |
| `map_codes` | Reads stored official correspondence records. | Does not mutate source codes or user data. | Mapping uses only bundled correspondence tables. |
| `export_choice_list` | Formats selected bundled records in memory. | Does not write files, publish forms or alter systems. | Export does not call ODK, Kobo, SurveyCTO or any external service. |

