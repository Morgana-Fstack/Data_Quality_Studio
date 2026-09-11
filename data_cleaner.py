"""Reusable data profiling and cleaning functions for the visual app."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def normalize_column_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return text or "coluna_sem_nome"


def make_unique_columns(columns) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for column in columns:
        base = normalize_column_name(column)
        seen[base] = seen.get(base, 0) + 1
        result.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
    return result


def profile_data(df: pd.DataFrame) -> dict[str, int]:
    blank_strings = int(
        sum(df[col].astype("string").str.strip().eq("").sum() for col in df.select_dtypes(include="object"))
    )
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": int(df.isna().sum().sum()) + blank_strings,
        "duplicates": int(df.duplicated().sum()),
    }


def inspect_data(df: pd.DataFrame) -> dict[str, int]:
    """Count visible problems so the interface can explain what will change."""
    object_columns = list(df.select_dtypes(include=["object", "string"]).columns)
    whitespace_cells = 0
    blank_strings = 0
    for col in object_columns:
        series = df[col].astype("string")
        whitespace_cells += int((series.notna() & series.ne(series.str.strip())).sum())
        blank_strings += int(series.str.strip().eq("").sum())
    normalized = make_unique_columns(df.columns)
    empty_rows = int(df.replace(r"^\s*$", pd.NA, regex=True).isna().all(axis=1).sum())
    empty_columns = int(df.replace(r"^\s*$", pd.NA, regex=True).isna().all(axis=0).sum())
    invalid_emails = 0
    for col in df.columns:
        if "mail" in normalize_column_name(col):
            values = df[col].astype("string").str.strip()
            invalid_emails += int((values.notna() & values.ne("") & ~values.str.match(EMAIL_PATTERN)).sum())
    return {
        "headers": sum(str(old) != new for old, new in zip(df.columns, normalized)),
        "whitespace": whitespace_cells,
        "blank_strings": blank_strings,
        "duplicates_after_trim": int(_trimmed_copy(df).duplicated().sum()),
        "empty_rows": empty_rows,
        "empty_columns": empty_columns,
        "invalid_emails": invalid_emails,
    }


def _trimmed_copy(df: pd.DataFrame) -> pd.DataFrame:
    candidate = df.copy()
    for col in candidate.select_dtypes(include=["object", "string"]).columns:
        candidate[col] = candidate[col].astype("string").str.strip()
    return candidate


def clean_dataframe(
    df: pd.DataFrame,
    *,
    normalize_headers: bool = True,
    trim_text: bool = True,
    empty_to_null: bool = True,
    remove_duplicates: bool = True,
    remove_empty_rows: bool = True,
    remove_empty_columns: bool = True,
    lowercase_emails: bool = True,
    title_columns: tuple[str, ...] = (),
) -> pd.DataFrame:
    cleaned = df.copy()
    if normalize_headers:
        cleaned.columns = make_unique_columns(cleaned.columns)
    if trim_text or empty_to_null:
        for col in cleaned.select_dtypes(include=["object", "string"]).columns:
            series = cleaned[col].astype("string")
            if trim_text:
                series = series.str.strip()
            if empty_to_null:
                series = series.replace(r"^\s*$", pd.NA, regex=True)
            cleaned[col] = series
    if lowercase_emails:
        for col in cleaned.columns:
            if "mail" in normalize_column_name(col):
                cleaned[col] = cleaned[col].astype("string").str.lower()
    for col in title_columns:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].astype("string").str.title()
    if remove_empty_rows:
        cleaned = cleaned.dropna(how="all")
    if remove_empty_columns:
        cleaned = cleaned.dropna(axis=1, how="all")
    if remove_duplicates:
        cleaned = cleaned.drop_duplicates()
    return cleaned.reset_index(drop=True)


def column_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a readable quality report for every column."""
    rows = max(len(df), 1)
    report = []
    for col in df.columns:
        values = df[col]
        blanks = values.astype("string").str.strip().eq("").sum() if values.dtype == "object" else 0
        missing = int(values.isna().sum() + blanks)
        invalid = 0
        if "mail" in normalize_column_name(col):
            text = values.astype("string").str.strip()
            invalid = int((text.notna() & text.ne("") & ~text.str.match(EMAIL_PATTERN)).sum())
        score = max(0, round(100 * (1 - ((missing + invalid) / rows))))
        report.append({
            "Coluna": str(col),
            "Tipo": str(values.dtype),
            "Preenchimento": f"{100 - round(100 * missing / rows)}%",
            "Vazios": missing,
            "Inválidos": invalid,
            "Valores únicos": int(values.nunique(dropna=True)),
            "Qualidade": f"{score}%",
        })
    return pd.DataFrame(report)


def quality_score(df: pd.DataFrame) -> int:
    """Calculate a transparent 0–100 score from completeness and validity."""
    if df.empty or not len(df.columns):
        return 0
    report = column_quality_report(df)
    scores = report["Qualidade"].str.rstrip("%").astype(int)
    duplicate_penalty = min(20, int(100 * df.duplicated().sum() / max(len(df), 1)))
    return max(0, int(round(scores.mean())) - duplicate_penalty)
