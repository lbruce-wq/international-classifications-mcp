from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable
from importlib.resources import files
from pathlib import Path

from .catalog import CONCEPT_RULES
from .models import (
    ChoiceListResponse,
    ClassificationRecommendation,
    ClassificationSummary,
    CodeItem,
    MappingItem,
    MappingResponse,
    RecommendationResponse,
    SearchResponse,
    ValidationItem,
    ValidationResponse,
)


def database_path() -> Path:
    return Path(files("international_classifications_mcp").joinpath("data/registry.sqlite"))


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(database_path())
    conn.row_factory = sqlite3.Row
    return conn


def list_classifications(
    domain: str | None = None, status: str | None = None
) -> list[ClassificationSummary]:
    query = "SELECT c.*, COUNT(k.code) AS code_count FROM classifications c LEFT JOIN codes k ON k.classification_id=c.id WHERE 1=1"
    args: list[str] = []
    if domain:
        query += " AND lower(c.domain) LIKE ?"
        args.append(f"%{domain.lower()}%")
    if status:
        query += " AND c.status=?"
        args.append(status)
    query += " GROUP BY c.id ORDER BY c.domain,c.acronym"
    with connect() as conn:
        return [ClassificationSummary(**dict(row)) for row in conn.execute(query, args)]


def get_classification(classification_id: str) -> ClassificationSummary:
    with connect() as conn:
        row = conn.execute(
            "SELECT c.*, COUNT(k.code) AS code_count FROM classifications c LEFT JOIN codes k ON k.classification_id=c.id WHERE c.id=? GROUP BY c.id",
            (classification_id,),
        ).fetchone()
    if not row:
        raise ValueError(
            f"Unknown classification_id '{classification_id}'. Run list_classifications first."
        )
    return ClassificationSummary(**dict(row))


def _fts_query(text: str) -> str:
    tokens = re.findall(r"[\w-]+", text, flags=re.UNICODE)
    return " OR ".join(f'"{token}"' for token in tokens[:12])


def search_codes(
    query: str, classification_ids: list[str] | None = None, limit: int = 20
) -> SearchResponse:
    if not query.strip():
        raise ValueError("query must not be empty")
    limit = max(1, min(limit, 100))
    where, args = [], []
    if classification_ids:
        where.append("c.classification_id IN ({})".format(",".join("?" * len(classification_ids))))
        args.extend(classification_ids)
    filters = (" AND " + " AND ".join(where)) if where else ""
    fts = _fts_query(query)
    sql = f"SELECT c.*, -bm25(codes_fts, 8.0, 4.0, 2.0, 1.0, 1.0) AS score FROM codes_fts JOIN codes c ON c.rowid=codes_fts.rowid WHERE codes_fts MATCH ?{filters} ORDER BY score DESC, length(c.code), c.code LIMIT ?"
    with connect() as conn:
        rows = conn.execute(sql, [fts, *args, limit]).fetchall()
    warnings = []
    if not rows:
        warnings.append(
            "No matching codes. Try a broader concept or run recommend_classifications first."
        )
    return SearchResponse(
        query=query,
        total=len(rows),
        results=[CodeItem(**dict(row)) for row in rows],
        warnings=warnings,
    )


def get_code(classification_id: str, code: str) -> CodeItem:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM codes WHERE classification_id=? AND code=? AND language='en'",
            (classification_id, code),
        ).fetchone()
    if not row:
        raise ValueError(f"Code '{code}' not found in {classification_id}.")
    return CodeItem(**dict(row))


def browse_hierarchy(
    classification_id: str, parent_code: str | None = None, limit: int = 200
) -> list[CodeItem]:
    with connect() as conn:
        if parent_code is None:
            rows = conn.execute(
                "SELECT * FROM codes WHERE classification_id=? AND parent_code IS NULL ORDER BY code LIMIT ?",
                (classification_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM codes WHERE classification_id=? AND parent_code=? ORDER BY code LIMIT ?",
                (classification_id, parent_code, limit),
            ).fetchall()
    return [CodeItem(**dict(row)) for row in rows]


def recommend(
    question_text: str,
    answer_options: list[str] | None = None,
    survey_context: str | None = None,
    limit: int = 5,
) -> RecommendationResponse:
    parts = [question_text, survey_context or "", *(answer_options or [])]
    haystack = " ".join(parts).casefold().replace("_", " ")
    candidates = []
    for cid, rule in CONCEPT_RULES.items():
        matched = [term for term in rule["positive"] if term in haystack]
        conflicts = [term for term in rule["negative"] if term in haystack]
        option_matches = sum(
            1
            for option in (answer_options or [])
            if any(term in option.casefold() for term in rule["positive"])
        )
        score = len(matched) * 20 + option_matches * 15 - len(conflicts) * 12
        if score <= 0:
            continue
        meta = get_classification(cid)
        confidence = "high" if score >= 55 else "medium" if score >= 25 else "low"
        candidates.append(
            ClassificationRecommendation(
                classification_id=cid,
                name=f"{meta.acronym} — {meta.name}",
                concept=rule["concept"],
                score=float(score),
                confidence=confidence,
                matched_evidence=sorted(set(matched)),
                reason=rule["reason"],
                usage_mode=rule["usage_mode"],
            )
        )
    candidates.sort(key=lambda x: (-x.score, x.classification_id))
    warnings = []
    if not candidates:
        warnings.append(
            "No deterministic concept rule matched. Provide answer options and module context, or search classifications by domain."
        )
    elif len(candidates) > 1 and candidates[0].score - candidates[1].score < 15:
        warnings.append(
            "The leading concepts are close. Inspect both and use surrounding questionnaire context before deciding."
        )
    return RecommendationResponse(
        recommendations=candidates[:limit],
        warnings=warnings,
        next_action="Call search_codes or browse_hierarchy only after selecting the intended classification concept.",
    )


def validate_codes(classification_id: str, codes: Iterable[str]) -> ValidationResponse:
    results = []
    for code in codes:
        try:
            item = get_code(classification_id, str(code))
            results.append(
                ValidationItem(input_code=str(code), valid=True, item=item, message="Valid code.")
            )
        except ValueError:
            results.append(
                ValidationItem(
                    input_code=str(code),
                    valid=False,
                    message="Code not present in this classification/version.",
                )
            )
    return ValidationResponse(
        classification_id=classification_id,
        valid_count=sum(x.valid for x in results),
        invalid_count=sum(not x.valid for x in results),
        results=results,
    )


def map_codes(source: str, target: str, codes: list[str]) -> MappingResponse:
    results = []
    with connect() as conn:
        for code in codes:
            rows = conn.execute(
                "SELECT * FROM correspondences WHERE source_classification_id=? AND target_classification_id=? AND source_code=?",
                (source, target, code),
            ).fetchall()
            targets = [row["target_code"] for row in rows]
            relationship = (
                "unmapped"
                if not rows
                else "exact"
                if len(rows) == 1 and rows[0]["relationship"] == "exact"
                else "one_to_many_or_changed"
                if len(rows) > 1
                else rows[0]["relationship"]
            )
            note = "; ".join(filter(None, (row["note"] for row in rows))) or None
            results.append(
                MappingItem(
                    source_code=code,
                    target_codes=targets,
                    relationship=relationship,
                    official=bool(rows),
                    note=note,
                )
            )
    warnings = [
        "A correspondence is not necessarily a safe automatic recode. Review splits, merges and changed definitions."
    ]
    return MappingResponse(
        source_classification=source,
        target_classification=target,
        results=results,
        warnings=warnings,
    )


def export_choices(
    classification_id: str, level: int | None = None, format: str = "xlsform", limit: int = 1000
) -> ChoiceListResponse:
    with connect() as conn:
        if level is None:
            rows = conn.execute(
                "SELECT code,label FROM codes WHERE classification_id=? ORDER BY code LIMIT ?",
                (classification_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT code,label FROM codes WHERE classification_id=? AND level=? ORDER BY code LIMIT ?",
                (classification_id, level, limit),
            ).fetchall()
    if format == "xlsform":
        output = [
            {"list_name": classification_id, "name": row["code"], "label": row["label"]}
            for row in rows
        ]
    else:
        output = [{"code": row["code"], "label": row["label"]} for row in rows]
    warning = (
        "Detailed occupational, industry, disease and crime classifications are normally post-coded rather than shown directly to respondents."
        if classification_id in {"isco08", "isic5", "icd11", "iccs1"}
        else "MICS response identifiers are question-specific discovery aids. Verify codes, wording, skips and country customisation against the cited MICS7 questionnaire before deployment."
        if classification_id == "mics7_responses"
        else None
    )
    return ChoiceListResponse(
        classification_id=classification_id,
        level=level,
        format=format,
        rows=output,
        warning=warning,
    )
