# Classification source audit (v0.5)

| Family | Custodian | Access used | Bundled coverage | Notes |
|---|---|---|---|---|
| ISIC Rev.5 | UNSD | Official CSV | Full hierarchy | Current structure; Rev.4 retained through official correspondence |
| CPC 3.0 | UNSD | Official CSV | Full hierarchy | Current product structure |
| COICOP 2018 | UNSD | Official XLSX | Full hierarchy and notes | Includes definitions, inclusions and exclusions |
| HS 2022 | WCO / UN Comtrade | UN Comtrade JSON | Full reference hierarchy | WCO legal text/terms remain authoritative |
| SITC Rev.4 | UNSD / UN Comtrade | JSON | Full hierarchy | Analytical trade classification |
| BEC Rev.5 | UNSD / UN Comtrade | JSON | Full hierarchy | Broad economic categories |
| ISIC 4→5 | UNSD | Official XLSX | Official correspondence | Splits/changes are not flattened |
| ISCO-08 | ILO | Official web/manual + verified open code/title mirror | Full code/title hierarchy | Definitions and index terms remain linked to ILO; source mirror is disclosed |
| ICSE-18 / ICSaW-18 | ILO | Official 20th ICLS resolution/manual | Operational category structures | Questionnaire concept rules included |
| ISCED 2011 | UNESCO UIS | Official manual | Core education levels | Detailed programme/attainment expansion remains pending; national mappings are out of scope |
| ISCED-F 2013 | UNESCO UIS | Official structure, accessed as attributed SKOS | Detailed field hierarchy | National field mappings are out of scope |
| ICC 1.1 | FAO | Official WCA 2020 Annex 4 | Full 196-item crop hierarchy | FAO Caliper remains the preferred linked-data reference when available |
| ICD-11 / ICF | WHO | WHO classification portal/API | Reference metadata | WHO licensing/API terms apply; no unlicensed mirror |
| ICCS 1.0 | UNODC | Official manual | Detailed 319-item structure | Narrative definitions remain linked |
| M49 | UNSD | Official HTML table | Full country/area codes | No national census or administrative codes |
| SDMX CDCL | SDMX Secretariat | Official registry/downloads | Expanded operational seed | A full Global Registry sync remains future work |
| MICS7 responses | UNICEF MICS | Official MICS7 questionnaires and customisation guidance | Curated question-specific codelists, v7.1 | Namespaced; verify wording, skips and country adaptations before deployment |
| COFOG / COPNI / COPP | UNSD | Official UNSD structures | Full title hierarchies | Purpose classifications for government, nonprofit institutions and producers |
| ICATUS 2016 | UNSD | Official UNSD structure | Full 724-item title hierarchy | International time-use activities |
| UNECE Recommendations 20/21 | UNECE, accessed via maintained Data Package mirrors | Attributed CSV distributions | Full code/title lists | Units of measure and package types; UNECE remains authoritative |
| DHS-8 responses | DHS Program | Official model questionnaires/manuals | Curated high-use answer lists | Not indicators; country questionnaires and recode manuals remain authoritative |
| Washington Group responses | Washington Group | Official question sets | Curated response scales | Question-set identity and version must be preserved |
| JMP WASH mappings | WHO/UNICEF JMP | Official core questions and ladders | Curated mappings and service ladders | Estimates and indicators belong in the indicators service |
| WHO vaccination responses | WHO | Official vaccination monitoring guidance | Curated evidence/record/status lists | Programme schedules remain country-specific |
| FAO WCA survey responses | FAO | World Programme for the Census of Agriculture 2020 | Curated land, livestock, holding and machinery lists | Distinct from the full ICC crop hierarchy |

The registry reports incomplete families as `seed`, `reference`, or `curated`. This is a deliberate safety feature, not a hidden gap.

Survey-ecosystem provenance rule: MICS, DHS, Washington Group, JMP, WHO vaccination and FAO WCA entries expose versioned questionnaire response codelists or categorical mappings only. They do not duplicate indicator definitions or estimates. Country adaptations, exact question wording, skips and collection protocols must be verified against the cited official instrument before deployment.
