from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
from datetime import UTC, datetime
from html import unescape
from pathlib import Path

from openpyxl import load_workbook

from .catalog import CLASSIFICATIONS, SEED_CODES

PACKAGE = Path(__file__).resolve().parent
PROJECT = PACKAGE.parents[1]
RAW = PROJECT / "data" / "raw"
OUTPUT = PACKAGE / "data" / "registry.sqlite"


SCHEMA = """
PRAGMA journal_mode=DELETE;
CREATE TABLE classifications (
  id TEXT PRIMARY KEY, acronym TEXT NOT NULL, name TEXT NOT NULL, version TEXT NOT NULL,
  custodian TEXT NOT NULL, domain TEXT NOT NULL, status TEXT NOT NULL, coverage TEXT NOT NULL,
  description TEXT NOT NULL, source_url TEXT NOT NULL, licence_note TEXT NOT NULL,
  retrieved_at TEXT, source_sha256 TEXT
);
CREATE TABLE codes (
  classification_id TEXT NOT NULL REFERENCES classifications(id), code TEXT NOT NULL,
  label TEXT NOT NULL, level INTEGER, parent_code TEXT, definition TEXT, includes TEXT,
  excludes TEXT, language TEXT NOT NULL DEFAULT 'en', PRIMARY KEY(classification_id, code, language)
);
CREATE INDEX codes_classification_idx ON codes(classification_id, code);
CREATE VIRTUAL TABLE codes_fts USING fts5(
  classification_id UNINDEXED, code, label, definition, includes, excludes,
  content='codes', content_rowid='rowid', tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER codes_ai AFTER INSERT ON codes BEGIN
  INSERT INTO codes_fts(rowid, classification_id, code, label, definition, includes, excludes)
  VALUES (new.rowid, new.classification_id, new.code, new.label, new.definition, new.includes, new.excludes);
END;
CREATE TABLE correspondences (
  source_classification_id TEXT NOT NULL, source_code TEXT NOT NULL,
  target_classification_id TEXT NOT NULL, target_code TEXT NOT NULL,
  relationship TEXT NOT NULL, official INTEGER NOT NULL DEFAULT 1, note TEXT,
  source_url TEXT NOT NULL
);
CREATE INDEX correspondence_idx ON correspondences(source_classification_id, target_classification_id, source_code);
CREATE TABLE build_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def _clean(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).replace("_x000D_", "").replace("\xa0", " ").strip()
    return text or None


def _parent_from_code(code: str, dotted: bool = False) -> str | None:
    if dotted:
        bits = code.split(".")
        return ".".join(bits[:-1]) or None
    if len(code) <= 1:
        return None
    return code[:-1]


def _insert_code(
    conn: sqlite3.Connection, cid: str, code: object, label: object, **kwargs: object
) -> None:
    c, lab = _clean(code), _clean(label)
    if not c or not lab:
        return
    conn.execute(
        "INSERT OR REPLACE INTO codes(classification_id,code,label,level,parent_code,definition,includes,excludes,language) VALUES(?,?,?,?,?,?,?,?,?)",
        (
            cid,
            c,
            lab,
            kwargs.get("level"),
            kwargs.get("parent_code"),
            _clean(kwargs.get("definition")),
            _clean(kwargs.get("includes")),
            _clean(kwargs.get("excludes")),
            kwargs.get("language", "en"),
        ),
    )


def _ingest_simple_csv(conn: sqlite3.Connection, cid: str, filename: str) -> None:
    with (RAW / filename).open(encoding="cp1252", newline="") as handle:
        rows = csv.reader(handle)
        next(rows)
        for code, label, *_ in rows:
            code = code.strip()
            _insert_code(
                conn, cid, code, label, level=len(code), parent_code=_parent_from_code(code)
            )


def _ingest_coicop(conn: sqlite3.Connection) -> None:
    ws = load_workbook(RAW / "coicop2018.xlsx", read_only=True, data_only=True).active
    rows = ws.iter_rows(values_only=True)
    next(rows)
    for code, title, intro, includes, also_includes, excludes, *_ in rows:
        if not code:
            continue
        code = str(code)
        combined = "\n".join(filter(None, [_clean(includes), _clean(also_includes)])) or None
        _insert_code(
            conn,
            "coicop2018",
            code,
            title,
            level=code.count(".") + 1,
            parent_code=_parent_from_code(code, True),
            definition=intro,
            includes=combined,
            excludes=excludes,
        )


def _ingest_comtrade(conn: sqlite3.Connection, cid: str, filename: str) -> None:
    payload = json.loads((RAW / filename).read_text(encoding="utf-8"))
    for item in payload["results"]:
        code = str(item["id"])
        if code == "TOTAL":
            continue
        label = re.sub(rf"^{re.escape(code)}\s*-\s*", "", str(item["text"])).strip()
        parent = item.get("parent")
        _insert_code(
            conn,
            cid,
            code,
            label,
            level=int(item.get("aggrlevel") or len(code)),
            parent_code=None if parent in (None, "#", "TOTAL") else str(parent),
        )


def _ingest_isic_mapping(conn: sqlite3.Connection) -> None:
    path = RAW / "isic4to5.xlsx"
    ws = load_workbook(path, read_only=True, data_only=True)["ISIC4-5"]
    rows = ws.iter_rows(values_only=True)
    next(rows)
    source_url = next(x["source_url"] for x in CLASSIFICATIONS if x["id"] == "isic4")
    for row in rows:
        if len(row) < 6 or not row[1] or not row[4]:
            continue
        source_code, source_label, target_code = str(row[1]), row[2], str(row[4])
        _insert_code(
            conn,
            "isic4",
            source_code,
            source_label,
            level=len(source_code),
            parent_code=_parent_from_code(source_code),
        )
        change = _clean(row[6]) if len(row) > 6 else None
        note = _clean(row[7]) if len(row) > 7 else None
        relationship = "exact" if not change else "official_correspondence"
        conn.execute(
            "INSERT INTO correspondences VALUES(?,?,?,?,?,?,?,?)",
            (
                "isic4",
                source_code,
                "isic5",
                target_code,
                relationship,
                1,
                note or change,
                source_url,
            ),
        )


def _ingest_isco(conn: sqlite3.Connection) -> None:
    for line in (RAW / "isco08.txt").read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        major = re.fullmatch(r"MAJOR GROUP\s+([0-9]):\s*(.+)", line, flags=re.IGNORECASE)
        if major:
            _insert_code(conn, "isco08", major.group(1), major.group(2), level=1)
            continue
        item = re.fullmatch(r"([0-9]{2,4})\s+(.+)", line)
        if item:
            code, label = item.groups()
            _insert_code(
                conn,
                "isco08",
                code,
                label,
                level=len(code),
                parent_code=_parent_from_code(code),
            )


def _strip_html(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value)).strip()


def _ingest_m49(conn: sqlite3.Connection) -> None:
    html = (RAW / "m49.csv").read_text(encoding="utf-8", errors="replace")
    table = re.search(r'<table id\s*=\s*"downloadTableEN".*?</table>', html, flags=re.DOTALL)
    if not table:
        raise ValueError("Official M49 English table not found")
    seen: set[str] = set()
    for row in re.findall(r"<tr>(.*?)</tr>", table.group(0), flags=re.DOTALL):
        cells = [
            _strip_html(cell) for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.DOTALL)
        ]
        if len(cells) < 12 or not re.fullmatch(r"\d{3}", cells[9] or ""):
            continue
        country, m49, iso2, iso3 = cells[8], cells[9], cells[10], cells[11]
        if m49 in seen:
            continue
        seen.add(m49)
        definition = f"ISO alpha-2: {iso2}; ISO alpha-3: {iso3}; UN region: {cells[3]}; sub-region: {cells[5]}"
        _insert_code(conn, "m49", m49, country, level=3, definition=definition)


def _ingest_mics7(conn: sqlite3.Connection) -> None:
    """Load the curated, round-specific MICS discovery layer.

    MICS modules, response codelists and indicators are deliberately separate
    classifications: similarly worded codes are not interchangeable objects.
    """
    payload = json.loads((RAW / "mics7_curated.json").read_text(encoding="utf-8"))
    for code, label, questionnaire, definition in payload["modules"]:
        _insert_code(
            conn,
            "mics7_modules",
            code,
            label,
            level=1,
            definition=definition,
            includes=f"Questionnaire/population: {questionnaire}",
        )
    for code, label, codelist, definition in payload["responses"]:
        _insert_code(
            conn,
            "mics7_responses",
            code,
            label,
            level=2,
            definition=definition,
            includes=f"Codelist: {codelist}",
        )
    for code, label, universe, definition in payload["indicators"]:
        _insert_code(
            conn,
            "mics7_indicators",
            code,
            label,
            level=2,
            definition=definition,
            includes=f"Reference population: {universe}",
        )


def _source_hash(cid: str) -> str | None:
    files = {
        "isic5": "isic5.csv",
        "cpc3": "cpc3.csv",
        "coicop2018": "coicop2018.xlsx",
        "hs2022": "hs2022.json",
        "sitc4": "sitc4.json",
        "bec5": "bec5.json",
        "isic4": "isic4to5.xlsx",
        "isco08": "isco08.txt",
        "m49": "m49.csv",
        "mics7_modules": "mics7_curated.json",
        "mics7_responses": "mics7_curated.json",
        "mics7_indicators": "mics7_curated.json",
    }
    filename = files.get(cid)
    if not filename or not (RAW / filename).exists():
        return None
    return hashlib.sha256((RAW / filename).read_bytes()).hexdigest()


def build(output: Path = OUTPUT) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    conn = sqlite3.connect(output)
    conn.executescript(SCHEMA)
    now = datetime.now(UTC).isoformat()
    for item in CLASSIFICATIONS:
        conn.execute(
            "INSERT INTO classifications VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (*item.values(), now, _source_hash(item["id"])),
        )
    for cid, rows in SEED_CODES.items():
        for code, label in rows:
            _insert_code(
                conn, cid, code, label, level=len(code), parent_code=_parent_from_code(code)
            )
    _ingest_simple_csv(conn, "isic5", "isic5.csv")
    _ingest_simple_csv(conn, "cpc3", "cpc3.csv")
    _ingest_coicop(conn)
    _ingest_comtrade(conn, "hs2022", "hs2022.json")
    _ingest_comtrade(conn, "sitc4", "sitc4.json")
    _ingest_comtrade(conn, "bec5", "bec5.json")
    _ingest_isic_mapping(conn)
    _ingest_isco(conn)
    _ingest_m49(conn)
    _ingest_mics7(conn)
    conn.execute("INSERT INTO build_metadata VALUES('registry_version','0.2.0')")
    conn.execute("INSERT INTO build_metadata VALUES('built_at',?)", (now,))
    conn.execute("INSERT INTO build_metadata VALUES('national_census_geography','out_of_scope')")
    conn.commit()
    conn.execute("ANALYZE")
    conn.execute("VACUUM")
    conn.close()
    return output


def main() -> None:
    path = build()
    print(path)


if __name__ == "__main__":
    main()
