"""Reusable data profiling and cleaning functions for the visual app."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd


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
    return {
        "headers": sum(str(old) != new for old, new in zip(df.columns, normalized)),
        "whitespace": whitespace_cells,
        "blank_strings": blank_strings,
        "duplicates_after_trim": int(_trimmed_copy(df).duplicated().sum()),
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
    if remove_duplicates:
        cleaned = cleaned.drop_duplicates()
    return cleaned.reset_index(drop=True)
