# Official statistical classifications for AI agents

Choosing codes for a questionnaire or dataset should be straightforward. In practice, international classifications are spread across different organisations, documents, spreadsheets and catalogue systems. Similar concepts can also require very different standards: occupation is not industry, employment status is not labour-force status, and a survey response list is not an analytical indicator.

Impact Engines' International Classifications MCP gives compatible AI assistants one consistent way to discover, inspect, search, validate, map and export official statistical classifications and survey response codelists.

## What is an MCP?

Model Context Protocol (MCP) is a standard way to connect an AI assistant to external tools and data. It is a little like giving the assistant a specialised set of search and retrieval functions that it can call while answering a question.

Without this connection, an assistant may have to rely on general web search or information learned during training. With the International Classifications MCP, it can search a versioned registry, inspect definitions and provenance, browse hierarchies and retrieve exact codes in a consistent, structured format. The user does not need to know in advance whether a question calls for ISCO, ISIC, ICSE, ISCED, MICS, the Washington Group or another standard.

## What it does

The MCP lets an AI agent:

- discover relevant classifications and response codelists from questionnaire text and answer options;
- return multiple relevant alternatives rather than silently choosing one for the user;
- search code titles, definitions, inclusions and exclusions;
- browse classification hierarchies and independent questionnaire codelists;
- retrieve and validate exact codes;
- apply stored official correspondence tables without flattening one-to-many mappings;
- export selected categories in a simple format or as XLSForm choice rows;
- retain the classification version, custodian, source and coverage limitations.

It does not invent codes, make hidden AI calls or treat similarly named standards as interchangeable. Recommendations are deterministic ranked shortlists, not automatic decisions.

## Why it is needed

Statistical classifications are easy to misuse. A survey designer might present hundreds of occupation codes directly to respondents when occupations should instead be post-coded from a job title and task description. An analyst might confuse a person's occupation with the industry of their workplace. A questionnaire programmer might combine unrelated MICS answer lists or use an analytical indicator as if it were a respondent choice.

This MCP gives an AI assistant a structured, provenance-first registry and explicit safeguards. It can explain why several standards may be relevant, show their different roles and let the user decide which classification or codelist fits the questionnaire or analysis.

The current production registry contains 31 classification families and 24,598 searchable records. Coverage includes major UN, ILO, UNESCO, FAO, UNODC, UNECE, WHO, UNICEF and other international standards, including ISIC, CPC, COICOP, HS, SITC, BEC, M49, ISCO, ICSE, ICSaW, ISCED, ISCED-F, ICCS, ICATUS, COFOG, COPNI, COPP and FAO's Indicative Crop Classification.

It also contains 30 separately selectable response codelists from MICS7, DHS-8, Washington Group question sets, WHO/UNICEF JMP WASH guidance, WHO vaccination survey guidance and FAO's World Programme for the Census of Agriculture.

## Set it up

The hosted endpoint is:

`https://classifications.impactengines.ai/mcp`

### ChatGPT desktop app / Codex

The easiest way is to paste this directly into a Codex chat:

> Install the International Classifications MCP from https://classifications.impactengines.ai/mcp

Codex should guide you through or complete the setup. If that does not work, add it manually in the ChatGPT desktop app:

1. Open **Settings > Plugins**.
2. Select the **MCPs** tab.
3. Choose **Add > Add MCP server**.
4. Enter `International Classifications` as the name.
5. Select **Streamable HTTP** as the type.
6. Enter `https://classifications.impactengines.ai/mcp` as the server URL.
7. Select **Save**.

No command line or API key is required. Start a new chat if the tools do not appear immediately, then ask Codex to confirm that the International Classifications MCP is connected.

### Claude

The easiest way is to paste this directly into a Claude chat:

> Install the International Classifications MCP from https://classifications.impactengines.ai/mcp

Claude should guide you through or complete the setup. If that does not work, add it manually in the Claude desktop app:

1. Open **Settings > Connectors**.
2. Select **Add**.
3. Enter `International Classifications` as the name.
4. Enter `https://classifications.impactengines.ai/mcp` as the MCP server URL.
5. Select **Continue**.
6. When Claude asks how to authenticate, select **No sign-in** to finish connecting it.

No command line or API key is required. Ask Claude to confirm that the International Classifications tools are available if you want to check the connection.

Other clients that support remote MCP servers can connect to the same URL using Streamable HTTP.

## How to ask it questions

Once connected, Codex or Claude may select the MCP automatically when a question clearly asks about statistical classifications, coding or questionnaire answer categories. For more reliable results, start with **"Using the International Classifications MCP..."**.

You do not normally need to name a classification in advance. Give the agent the question text, answer options and survey context. The MCP can return the relevant alternatives and explain their different purposes.

## Example prompts

> Using the International Classifications MCP, review these employment questions and identify every relevant international classification. Explain the difference between labour-force status, status in employment, occupation and industry before recommending how each question should be coded.

> I ask respondents for their job title and main tasks. Find the relevant ISCO-08 categories for a primary-school teacher and a nurse, include the hierarchy and source, and explain why the detailed codes should normally be assigned after interview rather than shown as answer options.

> What response lists could I use for a child-functioning question? Compare the relevant MICS7 and Washington Group codelists and let me choose rather than selecting one automatically.

> Find all relevant response codelists for vaccination evidence, including MICS, DHS and WHO alternatives. Show the options, versions and provenance, and explain any differences.

> Validate these ISIC Rev.4 codes, map them to ISIC Rev.5 and preserve any one-to-many mapping warnings.

> Export the MICS7 birth-registration response list as XLSForm choices. Use only the selected birth-registration codelist and do not combine it with unrelated MICS options.

> Which standard should I use for the field of a respondent's degree? Show the relevant ISCED-F hierarchy and explain how it differs from ISCED education levels.

## What it deliberately leaves out

National census and administrative geography codes are out of scope because they change frequently and there is no single authoritative global registry for them.

MICS and other survey ecosystems are represented by versioned response categories and categorical mappings. Analytical indicator definitions, numerators, denominators and published estimates belong in the separate Development Indicators MCP.

Some large standards have licensing or access restrictions. Reference-only entries are labelled clearly and are never presented as complete local code lists.

## Open source

The complete source code is available under the permissive MIT License. You can inspect the deterministic ranking rules and safeguards, review source provenance, contribute corrections, fork the project or host your own copy with Docker and Cloudflare Workers.

GitHub: **https://github.com/lbruce-wq/international-classifications-mcp**

The hosted service is production-ready for controlled public use. Feedback on classification coverage, questionnaire codelists, recommendation quality and real survey-design workflows is welcome.
