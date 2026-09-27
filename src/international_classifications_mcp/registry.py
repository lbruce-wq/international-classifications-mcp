from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable
from importlib.resources import files
from pathlib import Path

from .catalog import CONCEPT_RULES
from .models import (
    ChoiceListResponse,
    Citation,
    ClassificationRecommendation,
    ClassificationSummary,
    CodeItem,
    CodelistSummary,
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


def _require_classification(classification_id: str) -> ClassificationSummary:
    return get_classification(classification_id)


def _validate_limit(limit: int, maximum: int) -> None:
    if not 1 <= limit <= maximum:
        raise ValueError(f"limit must be between 1 and {maximum}.")


def _code_select(score: bool = False) -> str:
    score_sql = ", -bm25(codes_fts, 8.0, 4.0, 2.0, 1.0, 1.0) AS score" if score else ""
    return (
        "SELECT c.*, m.version AS classification_version, m.name AS source_title, "
        f"m.source_url{score_sql} FROM codes c JOIN classifications m ON m.id=c.classification_id"
    )


def _fts_query(text: str) -> str:
    tokens = re.findall(r"[^\W_]+", text, flags=re.UNICODE)
    stopwords = {"a", "an", "the", "of", "for", "to", "no", "such", "code"}
    aliases = {
        "diarrhoea": ["illness", "care"], "diarrhea": ["illness", "care"],
        "fever": ["illness", "care"], "vaccination": ["immunisation", "vaccine"],
        "breastfeeding": ["breastfed", "breastfeed"], "sanitation": ["toilet", "latrine"],
    }
    expanded: list[str] = []
    for token in tokens[:12]:
        folded = token.casefold()
        if folded in stopwords:
            continue
        stem = folded[:-1] if len(folded) > 4 and folded.endswith(("s", "e")) else folded
        expanded.extend([folded, f"{stem}*"])
        expanded.extend(aliases.get(folded, []))
    return " OR ".join(dict.fromkeys(f'"{term}"' if not term.endswith("*") else term for term in expanded))


MICS_CODELIST_TERMS = {
    "BR.STATUS": ("birth registration", "registered birth", "birth certificate"),
    "CD.METHOD_GROUP": ("child discipline", "disciplinary method", "physical punishment", "psychological aggression"),
    "CF.DIFFICULTY": ("child functioning", "functioning difficulty", "difficulty scale"),
    "ED.ATTEND": ("school attendance", "currently attending", "never attended"),
    "IM.SOURCE": ("vaccination source", "vaccination evidence", "vaccination card", "immunisation source"),
    "SEX": ("sex", "male female"),
    "WS_SAN": ("sanitation facility", "toilet facility", "latrine type"),
    "WS_SOURCE": ("drinking water source", "water source", "main source of drinking water"),
    "YN": ("yes no", "yes/no", "don't know", "dont know"),
}


def _infer_mics_codelist(text: str) -> str | None:
    folded = text.casefold().replace("-", " ")
    for codelist_id, terms in MICS_CODELIST_TERMS.items():
        if any(term in folded for term in terms):
            return codelist_id
    return None


def list_codelists(classification_id: str) -> list[CodelistSummary]:
    _require_classification(classification_id)
    with connect() as conn:
        rows = conn.execute(
            "SELECT l.*, COUNT(c.code) AS option_count FROM codelists l LEFT JOIN codes c ON c.classification_id=l.classification_id AND c.codelist_id=l.codelist_id WHERE l.classification_id=? GROUP BY l.classification_id,l.codelist_id ORDER BY l.codelist_id",
            (classification_id,),
        ).fetchall()
    return [CodelistSummary(**dict(row)) for row in rows]


def search_codes(
    query: str, classification_ids: list[str] | None = None, limit: int = 20, codelist_id: str | None = None
) -> SearchResponse:
    if not query.strip():
        raise ValueError("query must not be empty")
    _validate_limit(limit, 100)
    if codelist_id and classification_ids is None:
        classification_ids = ["mics7_responses"]
    where, args = [], []
    if classification_ids:
        for classification_id in classification_ids:
            _require_classification(classification_id)
        where.append("c.classification_id IN ({})".format(",".join("?" * len(classification_ids))))
        args.extend(classification_ids)
    inferred_codelist = None
    if codelist_id:
        if classification_ids != ["mics7_responses"]:
            raise ValueError("codelist_id currently requires classification_ids=['mics7_responses'].")
        available = {item.codelist_id for item in list_codelists("mics7_responses")}
        if codelist_id not in available:
            raise ValueError(f"Unknown codelist_id '{codelist_id}'. Run list_codelists first.")
        where.append("c.codelist_id=?")
        args.append(codelist_id)
    elif classification_ids == ["mics7_responses"]:
        inferred_codelist = _infer_mics_codelist(query)
        if inferred_codelist:
            where.append("c.codelist_id=?")
            args.append(inferred_codelist)
    filters = (" AND " + " AND ".join(where)) if where else ""
    fts = _fts_query(query)
    if not fts:
        return SearchResponse(query=query, total=0, results=[], warnings=["No searchable letters or numbers were supplied."])
    sql = f"SELECT c.*, m.version AS classification_version, m.name AS source_title, m.source_url, -bm25(codes_fts, 8.0, 4.0, 2.0, 1.0, 1.0) AS score FROM codes_fts JOIN codes c ON c.rowid=codes_fts.rowid JOIN classifications m ON m.id=c.classification_id WHERE codes_fts MATCH ?{filters} ORDER BY score DESC, length(c.code), c.code LIMIT ?"
    with connect() as conn:
        rows = conn.execute(sql, [fts, *args, limit]).fetchall()
    warnings = []
    if not rows:
        warnings.append(
            "No matching codes. Try a broader concept or run recommend_classifications first."
        )
    elif inferred_codelist:
        warnings.append(f"Restricted results to inferred MICS codelist {inferred_codelist}. Pass codelist_id explicitly to confirm or override.")
    return SearchResponse(
        query=query,
        total=len(rows),
        results=[CodeItem(**dict(row)) for row in rows],
        warnings=warnings,
    )


def get_code(classification_id: str, code: str) -> CodeItem:
    _require_classification(classification_id)
    with connect() as conn:
        row = conn.execute(
            _code_select() + " WHERE c.classification_id=? AND c.code=? AND c.language='en'",
            (classification_id, code),
        ).fetchone()
    if not row:
        raise ValueError(f"Code '{code}' not found in {classification_id}.")
    return CodeItem(**dict(row))


def browse_hierarchy(
    classification_id: str, parent_code: str | None = None, limit: int = 200
) -> list[CodeItem]:
    _require_classification(classification_id)
    _validate_limit(limit, 500)
    with connect() as conn:
        if classification_id == "mics7_responses" and parent_code is None:
            meta = get_classification(classification_id)
            return [CodeItem(classification_id=classification_id, code=item.codelist_id, label=item.title, level=1, definition=item.concept, classification_version=meta.version, source_title=meta.name, source_url=item.source_url, codelist_id=item.codelist_id) for item in list_codelists(classification_id)[:limit]]
        if parent_code is None:
            rows = conn.execute(
                _code_select() + " WHERE c.classification_id=? AND c.parent_code IS NULL ORDER BY c.code LIMIT ?",
                (classification_id, limit),
            ).fetchall()
            if not rows:
                rows = conn.execute(
                    _code_select() + " WHERE c.classification_id=? AND c.level=(SELECT MIN(level) FROM codes WHERE classification_id=?) ORDER BY c.code LIMIT ?",
                    (classification_id, classification_id, limit),
                ).fetchall()
        else:
            rows = conn.execute(
                _code_select() + " WHERE c.classification_id=? AND c.parent_code=? ORDER BY c.code LIMIT ?",
                (classification_id, parent_code, limit),
            ).fetchall()
    return [CodeItem(**dict(row)) for row in rows]


def recommend(
    question_text: str,
    answer_options: list[str] | None = None,
    survey_context: str | None = None,
    limit: int = 5,
) -> RecommendationResponse:
    _validate_limit(limit, 20)
    parts = [question_text, survey_context or "", *(answer_options or [])]
    haystack = " ".join(parts).casefold().replace("_", " ").replace("-", " ").replace("—", " ")
    indicator_request = "mics" in haystack and any(term in haystack for term in ("indicator", "proportion", "percentage", "prevalence", "rate", "numerator", "denominator"))
    candidates = []
    for cid, rule in CONCEPT_RULES.items():
        if cid == "mics7_responses" and indicator_request:
            continue
        matched = [term for term in rule["positive"] if term in haystack]
        conflicts = [term for term in rule["negative"] if term in haystack]
        option_matches = sum(
            1
            for option in (answer_options or [])
            if any(term in option.casefold() for term in rule["positive"])
        )
        priority_matches = [term for term in rule.get("priority", []) if term in haystack]
        score = len(matched) * 20 + len(priority_matches) * 60 + option_matches * 15 - len(conflicts) * 12
        if score <= 0:
            continue
        meta = get_classification(cid)
        codelist_id = _infer_mics_codelist(haystack) if cid == "mics7_responses" else None
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
                classification_version=meta.version,
                source_title=meta.name,
                source_url=meta.source_url,
                codelist_id=codelist_id,
            )
        )
    candidates.sort(key=lambda x: (-x.score, x.classification_id))
    warnings = []
    if not candidates:
        if indicator_request:
            warnings.append("This is a MICS analytical-indicator request. Use the Development Indicators MCP; this registry intentionally exposes only MICS questionnaire response codelists.")
        else:
            warnings.append("No deterministic concept rule matched. Provide answer options and module context, or search classifications by domain.")
    elif len(candidates) > 1 and candidates[0].score - candidates[1].score < 15:
        warnings.append(
            "The leading concepts are close. Inspect both and use surrounding questionnaire context before deciding."
        )
    next_action = "Call search_codes or browse_hierarchy only after selecting the intended classification concept."
    if not candidates and indicator_request:
        next_action = "Use the Development Indicators MCP to discover and retrieve the MICS indicator definition."
    elif candidates and candidates[0].classification_id == "mics7_responses" and candidates[0].codelist_id:
        next_action = f"Search or export MICS codelist {candidates[0].codelist_id}; do not combine it with other response lists."
    return RecommendationResponse(
        recommendations=candidates[:limit],
        warnings=warnings,
        next_action=next_action,
    )


def validate_codes(classification_id: str, codes: Iterable[str]) -> ValidationResponse:
    _require_classification(classification_id)
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
    source_meta = _require_classification(source)
    target_meta = _require_classification(target)
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
            note = "; ".join(dict.fromkeys(filter(None, (row["note"] for row in rows)))) or None
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
        sources=[
            Citation(title=f"{source_meta.name}, version {source_meta.version}", url=source_meta.source_url, custodian=source_meta.custodian),
            Citation(title=f"{target_meta.name}, version {target_meta.version}", url=target_meta.source_url, custodian=target_meta.custodian),
        ],
        warnings=warnings,
    )


def export_choices(
    classification_id: str, level: int | None = None, format: str = "xlsform", limit: int = 1000, codelist_id: str | None = None
) -> ChoiceListResponse:
    meta = _require_classification(classification_id)
    _validate_limit(limit, 10000)
    selected_codelist = None
    if classification_id == "mics7_responses" and not codelist_id:
        raise ValueError("codelist_id is required for MICS exports. Run list_codelists('mics7_responses') and select one list.")
    if codelist_id:
        available = {item.codelist_id: item for item in list_codelists(classification_id)}
        if codelist_id not in available:
            raise ValueError(f"Unknown codelist_id '{codelist_id}'. Run list_codelists first.")
        selected_codelist = available[codelist_id]
    with connect() as conn:
        if codelist_id:
            rows = conn.execute("SELECT code,label FROM codes WHERE classification_id=? AND codelist_id=? ORDER BY code LIMIT ?", (classification_id, codelist_id, limit)).fetchall()
        elif level is None:
            levels = [row[0] for row in conn.execute("SELECT DISTINCT level FROM codes WHERE classification_id=? AND level IS NOT NULL ORDER BY level", (classification_id,))]
            effective_level = levels[0] if len(levels) > 1 else None
            rows = conn.execute(
                "SELECT code,label FROM codes WHERE classification_id=? AND (? IS NULL OR level=?) ORDER BY code LIMIT ?",
                (classification_id, effective_level, effective_level, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT code,label FROM codes WHERE classification_id=? AND level=? ORDER BY code LIMIT ?",
                (classification_id, level, limit),
            ).fetchall()
    if format == "xlsform":
        output = [
            {"list_name": codelist_id or classification_id, "name": row["code"], "label": row["label"]}
            for row in rows
        ]
    else:
        output = [{"code": row["code"], "label": row["label"]} for row in rows]
    warnings = []
    if level is None and 'effective_level' in locals() and effective_level is not None:
        warnings.append(f"This hierarchy has multiple levels; the export defaulted safely to top level {effective_level}. Specify level explicitly for another level.")
    warning = (
        "Detailed occupational, industry, disease and crime classifications are normally post-coded rather than shown directly to respondents."
        if classification_id in {"isco08", "isic5", "icd11", "iccs1"}
        else "MICS response identifiers are question-specific discovery aids. Verify codes, wording, skips and country customisation against the cited MICS7 questionnaire before deployment."
        if classification_id == "mics7_responses"
        else None
    )
    if warning:
        warnings.append(warning)
    warnings.append(f"Source: {meta.name}, version {meta.version}, {meta.source_url}")
    return ChoiceListResponse(
        classification_id=classification_id,
        codelist_id=codelist_id,
        codelist_title=selected_codelist.title if selected_codelist else None,
        option_count=len(output),
        level=level,
        format=format,
        rows=output,
        warning=" ".join(warnings),
    )
