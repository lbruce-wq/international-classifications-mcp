from __future__ import annotations

import json
import os
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

from . import __version__
from .models import (
    ChoiceListResponse,
    ClassificationSummary,
    CodeItem,
    MappingResponse,
    RecommendationResponse,
    SearchResponse,
    ValidationResponse,
)
from .registry import browse_hierarchy as registry_browse_hierarchy
from .registry import export_choices, recommend
from .registry import get_classification as registry_get_classification
from .registry import get_code as registry_get_code
from .registry import list_classifications as registry_list_classifications
from .registry import map_codes as registry_map_codes
from .registry import search_codes as registry_search_codes
from .registry import validate_codes as registry_validate_codes


class CompatibleFastMCP(FastMCP):
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        result = await super().call_tool(name, arguments)
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
            structured = result[1]
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(structured, ensure_ascii=False, separators=(",", ":")),
                    )
                ],
                structuredContent=structured,
            )
        return result


mcp = CompatibleFastMCP(
    "International Classifications MCP",
    instructions=(
        "Deterministic access to official international statistical classifications. No LLM or paid AI runs inside this server. "
        "Distinguish occupation (ISCO), industry (ISIC), status in employment (ICSE), labour-force status, education level (ISCED), and field of study (ISCED-F). "
        "For questionnaire review, call recommend_classifications with the question, answer options and context; then inspect the selected classification before requesting codes. "
        "Do not dump a full detailed classification into a questionnaire unless explicitly requested. Detailed occupation, industry, disease and crime schemes are normally post-coded. "
        "Mappings may be one-to-many or definition-changing: preserve warnings and citations. National census geography is out of scope."
    ),
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8000")),
)
mcp._mcp_server.version = __version__


@mcp.tool()
def list_classifications(
    domain: str | None = None, status: str | None = None
) -> list[ClassificationSummary]:
    """List classification families, versions, custodians, coverage and licensing notes. Start here when the correct standard is unknown."""
    return registry_list_classifications(domain, status)


@mcp.tool()
def get_classification(classification_id: str) -> ClassificationSummary:
    """Get authoritative metadata and coverage for one classification_id returned by list_classifications."""
    return registry_get_classification(classification_id)


@mcp.tool()
def recommend_classifications(
    question_text: str,
    answer_options: list[str] | None = None,
    survey_context: str | None = None,
    limit: int = 5,
) -> RecommendationResponse:
    """Deterministically rank applicable classification concepts for a questionnaire item. Include answer options and module context. This uses curated rules, not an LLM."""
    return recommend(question_text, answer_options, survey_context, limit)


@mcp.tool()
def search_codes(
    query: str, classification_ids: list[str] | None = None, limit: int = 20
) -> SearchResponse:
    """Full-text search code labels, definitions, inclusions and exclusions. Prefer specifying classification_ids after concept discovery."""
    return registry_search_codes(query, classification_ids, limit)


@mcp.tool()
def get_code_definition(classification_id: str, code: str) -> CodeItem:
    """Retrieve one exact code, label, hierarchy position and available explanatory notes."""
    return registry_get_code(classification_id, code)


@mcp.tool()
def browse_hierarchy(
    classification_id: str, parent_code: str | None = None, limit: int = 200
) -> list[CodeItem]:
    """Browse top-level items or immediate children under parent_code without returning the whole classification."""
    return registry_browse_hierarchy(classification_id, parent_code, limit)


@mcp.tool()
def validate_codes(classification_id: str, codes: list[str]) -> ValidationResponse:
    """Validate exact codes against one named classification version."""
    return registry_validate_codes(classification_id, codes)


@mcp.tool()
def map_codes(
    source_classification_id: str, target_classification_id: str, codes: list[str]
) -> MappingResponse:
    """Apply official stored correspondences and expose splits, merges, changed meanings and unmapped codes. Never assume one-to-one equivalence."""
    return registry_map_codes(source_classification_id, target_classification_id, codes)


@mcp.tool()
def export_choice_list(
    classification_id: str,
    level: int | None = None,
    format: Literal["xlsform", "simple"] = "xlsform",
    limit: int = 1000,
) -> ChoiceListResponse:
    """Return a structured choice list at a selected hierarchy level. Respect the warning when a standard should be post-coded instead."""
    return export_choices(classification_id, level, format, limit)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
