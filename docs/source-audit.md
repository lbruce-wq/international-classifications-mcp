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

The registry reports incomplete families as `seed` or `reference`. This is a deliberate safety feature, not a hidden gap.
