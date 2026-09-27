from __future__ import annotations

import json
import os
from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from pydantic import Field

from . import __version__
from .models import (
    ChoiceListResponse,
    ClassificationSummary,
    CodeItem,
    CodelistSummary,
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
from .registry import list_codelists as registry_list_codelists
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
        "For questionnaire review, call recommend_classifications with the question, answer options and context. Present every returned relevant alternative and its role; ranking is not an automatic selection. "
        "MICS7 content is limited to question-specific response codelists. MICS indicator definitions belong in a development-indicators service, not this classification registry. Never route an indicator, proportion, prevalence or rate request to an answer codelist. "
        "Before exporting MICS responses, call list_codelists and select exactly one codelist_id; never merge independent MICS answer lists. "
        "Do not dump a full detailed classification into a questionnaire unless explicitly requested. Detailed occupation, industry, disease and crime schemes are normally post-coded. "
        "Mappings may be one-to-many or definition-changing: preserve warnings and citations. National census geography is out of scope."
    ),
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8000")),
)
mcp._mcp_server.version = __version__
READ_ONLY = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False
)


@mcp.tool(title="List classifications", annotations=READ_ONLY)
def list_classifications(
    domain: str | None = None, status: str | None = None
) -> list[ClassificationSummary]:
    """List classification families, versions, custodians, coverage and licensing notes. Start here when the correct standard is unknown."""
    return registry_list_classifications(domain, status)


@mcp.tool(title="Get classification metadata", annotations=READ_ONLY)
def get_classification(classification_id: str) -> ClassificationSummary:
    """Get authoritative metadata and coverage for one classification_id returned by list_classifications."""
    return registry_get_classification(classification_id)


@mcp.tool(title="List codelists", annotations=READ_ONLY)
def list_codelists(classification_id: str) -> list[CodelistSummary]:
    """List independent option lists within a classification before searching or exporting one list."""
    return registry_list_codelists(classification_id)


@mcp.tool(title="Recommend classifications", annotations=READ_ONLY)
def recommend_classifications(
    question_text: str,
    answer_options: list[str] | None = None,
    survey_context: str | None = None,
    limit: Annotated[int, Field(ge=1, le=20)] = 5,
) -> RecommendationResponse:
    """Return a deterministic ranked shortlist of all relevant classification concepts and codelists. Ranking supports user choice; it is not an automatic selection. Include answer options and context."""
    return recommend(question_text, answer_options, survey_context, limit)


@mcp.tool(title="Search classification codes", annotations=READ_ONLY)
def search_codes(
    query: str,
    classification_ids: list[str] | None = None,
    codelist_id: str | None = None,
    limit: Annotated[int, Field(ge=1, le=100)] = 20,
) -> SearchResponse:
    """Full-text search labels and notes. Results restrict to one option list only when codelist_id is explicitly supplied."""
    return registry_search_codes(query, classification_ids, limit, codelist_id)


@mcp.tool(title="Get code definition", annotations=READ_ONLY)
def get_code_definition(classification_id: str, code: str) -> CodeItem:
    """Retrieve one exact code, label, hierarchy position and available explanatory notes."""
    return registry_get_code(classification_id, code)


@mcp.tool(title="Browse classification hierarchy", annotations=READ_ONLY)
def browse_hierarchy(
    classification_id: str,
    parent_code: str | None = None,
    limit: Annotated[int, Field(ge=1, le=500)] = 200,
) -> list[CodeItem]:
    """Browse top-level items or immediate children under parent_code without returning the whole classification."""
    return registry_browse_hierarchy(classification_id, parent_code, limit)


@mcp.tool(title="Validate classification codes", annotations=READ_ONLY)
def validate_codes(
    classification_id: str, codes: Annotated[list[str], Field(min_length=1)]
) -> ValidationResponse:
    """Validate exact codes against one named classification version."""
    return registry_validate_codes(classification_id, codes)


@mcp.tool(title="Map codes between versions", annotations=READ_ONLY)
def map_codes(
    source_classification_id: str,
    target_classification_id: str,
    codes: Annotated[list[str], Field(min_length=1)],
) -> MappingResponse:
    """Apply official stored correspondences and expose splits, merges, changed meanings and unmapped codes. Never assume one-to-one equivalence."""
    return registry_map_codes(source_classification_id, target_classification_id, codes)


@mcp.tool(title="Export a choice list", annotations=READ_ONLY)
def export_choice_list(
    classification_id: str,
    level: int | None = None,
    codelist_id: str | None = None,
    format: Literal["xlsform", "simple"] = "xlsform",
    limit: Annotated[int, Field(ge=1, le=10000)] = 1000,
) -> ChoiceListResponse:
    """Return a structured choice list at a selected hierarchy level. MICS exports require one codelist_id and never merge unrelated answer lists."""
    return export_choices(classification_id, level, format, limit, codelist_id)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
