# Tier-1 source audit

| Family | Custodian | Access used | Bundled coverage | Notes |
|---|---|---|---|---|
| ISIC Rev.5 | UNSD | Official CSV | Full hierarchy | Current structure; Rev.4 retained through official correspondence |
| CPC 3.0 | UNSD | Official CSV | Full hierarchy | Current product structure |
| COICOP 2018 | UNSD | Official XLSX | Full hierarchy and notes | Includes definitions, inclusions and exclusions |
| HS 2022 | WCO / UN Comtrade | UN Comtrade JSON | Full reference hierarchy | WCO legal text/terms remain authoritative |
| SITC Rev.4 | UNSD / UN Comtrade | JSON | Full hierarchy | Analytical trade classification |
| BEC Rev.5 | UNSD / UN Comtrade | JSON | Full hierarchy | Broad economic categories |
| ISIC 4→5 | UNSD | Official XLSX | Official correspondence | Splits/changes are not flattened |
| ISCO-08 | ILO | Official web/manual + verified open code/title mirror | Full code/title hierarchy | Definitions remain linked to ILO; source mirror is disclosed |
| ICSE-18 / ICSaW-18 | ILO | Official standard | Core operational categories / reference | Questionnaire concept rules included |
| ISCED / ISCED-F | UNESCO UIS | Official manuals | Core level/broad-field structures | National mappings are out of scope |
| ICC 1.1 | FAO Caliper | Linked-data portal | Reference metadata | Add full adapter after confirming stable machine endpoint and terms |
| ICD-11 / ICF | WHO | WHO classification portal/API | Reference metadata | WHO licensing/API terms apply; no unlicensed mirror |
| ICCS 1.0 | UNODC | Official manual | Top-level structure | Detailed definitions remain linked |
| M49 | UNSD | Official HTML table | Full country/area codes | No national census or administrative codes |
| SDMX CDCL | SDMX Secretariat | Official registry/downloads | Selected operational codes | Expand via Global Registry adapter |
| MICS7 modules | UNICEF MICS | Official MICS7 tools page / questionnaire topics | Curated discovery layer, v7.1.9 | Modules are not classifications or answer codes |
| MICS7 responses | UNICEF MICS | Official MICS7 questionnaires and customisation guidance | Curated question-specific codelists, v7.1 | Namespaced; verify wording, skips and country adaptations before deployment |
| MICS7 indicators | UNICEF MICS | Official Indicators and Definitions v7.1.9 | Selected high-use concepts and derivation notes | Official specification remains authoritative |

The registry reports incomplete families as `seed`, `reference`, or `curated`. This is a deliberate safety feature, not a hidden gap.

MICS provenance rule: this registry exposes only question-specific response categories. Modules are discovery metadata outside the classification catalogue, and derived indicators belong in the separate development-indicators service. Response categories carry their MICS round/version; MICS6 and MICS7 content must not be merged without an explicit correspondence review.
