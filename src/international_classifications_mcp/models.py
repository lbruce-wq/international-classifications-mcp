from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    title: str
    url: str
    custodian: str
    retrieved_at: str | None = None


class ClassificationSummary(BaseModel):
    id: str
    name: str
    version: str
    acronym: str
    custodian: str
    domain: str
    status: str
    coverage: str
    code_count: int = 0
    description: str
    source_url: str
    licence_note: str


class CodeItem(BaseModel):
    classification_id: str
    code: str
    label: str
    level: int | None = None
    parent_code: str | None = None
    definition: str | None = None
    includes: str | None = None
    excludes: str | None = None
    language: str = "en"
    score: float | None = None
    classification_version: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    codelist_id: str | None = None


class CodelistSummary(BaseModel):
    classification_id: str
    codelist_id: str
    title: str
    concept: str
    source_version: str
    option_count: int
    warning: str
    source_url: str


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[CodeItem]
    warnings: list[str] = Field(default_factory=list)


class ClassificationRecommendation(BaseModel):
    classification_id: str
    name: str
    concept: str
    score: float
    confidence: Literal["high", "medium", "low"]
    matched_evidence: list[str]
    reason: str
    usage_mode: str
    classification_version: str
    source_title: str
    source_url: str
    codelist_id: str | None = None


class RecommendationResponse(BaseModel):
    recommendations: list[ClassificationRecommendation]
    warnings: list[str] = Field(default_factory=list)
    next_action: str


class ValidationItem(BaseModel):
    input_code: str
    valid: bool
    item: CodeItem | None = None
    message: str


class ValidationResponse(BaseModel):
    classification_id: str
    valid_count: int
    invalid_count: int
    results: list[ValidationItem]


class MappingItem(BaseModel):
    source_code: str
    target_codes: list[str]
    relationship: str
    official: bool
    note: str | None = None


class MappingResponse(BaseModel):
    source_classification: str
    target_classification: str
    results: list[MappingItem]
    sources: list[Citation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ChoiceListResponse(BaseModel):
    classification_id: str
    codelist_id: str | None = None
    codelist_title: str | None = None
    option_count: int
    level: int | None
    format: str
    rows: list[dict[str, Any]]
    warning: str | None = None
