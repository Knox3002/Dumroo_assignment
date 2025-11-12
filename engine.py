# engine.py
# Simple CSV loader + scoping helpers for dumroo

import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any

DATA_FILE = "Dataset.csv"

def parse_bool(v: str) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes")

def parse_date(v: str):
    try:
        return datetime.strptime(v.strip(), "%Y-%m-%d").date()
    except Exception:
        return None

def load_rows() -> List[Dict[str, Any]]:
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            row = {
                "student_id": r.get("student_id"),
                "name": r.get("name"),
                "grade": int(r.get("grade")) if r.get("grade") else None,
                "class": r.get("class"),
                "region": r.get("region"),
                "homework_submitted": parse_bool(r.get("homework_submitted", "False")),
                "quiz_date": parse_date(r.get("quiz_date", "")),
                "quiz_name": r.get("quiz_name"),
                "quiz_score": int(r.get("quiz_score")) if r.get("quiz_score") else None,
                "date": parse_date(r.get("date", "")),
            }
            rows.append(row)
    return rows

def apply_scope(rows: List[Dict[str, Any]], grade=None, class_=None, region=None):
    """Return only rows matching non-null scope values."""
    out = []
    for r in rows:
        if grade is not None and r.get("grade") != grade:
            continue
        if class_ is not None and str(r.get("class")).upper() != str(class_).upper():
            continue
        if region is not None and r.get("region").lower() != str(region).lower():
            continue
        out.append(r)
    return out

def rows_to_context(rows: List[Dict[str, Any]], max_rows=50) -> str:
    """Turn rows into a small text block for LLM context (limited)."""
    lines = []
    for i, r in enumerate(rows):
        if i >= max_rows:
            break
        lines.append(f"- {r['student_id']}: {r['name']}, Grade {r['grade']}, Class {r['class']}, Region {r['region']}, HomeworkSubmitted={r['homework_submitted']}, Quiz={r['quiz_name']} on {r['quiz_date']}, Score={r['quiz_score']}, Date={r['date']}")
    if not lines:
        return "NO_ROWS"
    return "\n".join(lines)