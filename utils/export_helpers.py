from datetime import date
from pathlib import Path

import pandas as pd


class ExportValidationError(Exception):
    """Raised when a DataFrame doesn't match its expected export contract."""
    pass


def validate_export(
    df: pd.DataFrame,
    expected_columns: list[str],
    grain_check_fn=None,
    grain_description: str = "",
    allow_extra_columns: bool = True,
    no_nulls_in: list[str] | None = None,
) -> None:
    errors = []

    missing = set(expected_columns) - set(df.columns)
    if missing:
        errors.append(f"Missing expected columns: {sorted(missing)}")

    if not allow_extra_columns:
        extra = set(df.columns) - set(expected_columns)
        if extra:
            errors.append(f"Unexpected extra columns: {sorted(extra)}")

    if len(df) == 0:
        errors.append("DataFrame is empty - expected at least one row")

    if grain_check_fn is not None:
        try:
            grain_ok = grain_check_fn(df)
        except Exception as e:
            grain_ok = False
            errors.append(f"Grain check raised an exception: {e}")
        else:
            if not grain_ok:
                desc = f" ({grain_description})" if grain_description else ""
                errors.append(f"Grain check failed{desc}")

    if no_nulls_in:
        for col in no_nulls_in:
            if col in df.columns and df[col].isna().any():
                null_count = int(df[col].isna().sum())
                errors.append(f"Column '{col}' has {null_count} unexpected null(s)")

    if errors:
        error_msg = "Export validation failed:\n  - " + "\n  - ".join(errors)
        raise ExportValidationError(error_msg)

    print(f"Export validated: {len(df)} rows, {len(df.columns)} columns")


def export_with_manifest_note(
    df: pd.DataFrame,
    output_path: str,
    grain: str,
    source_notebook: str,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

    print(f"\nWritten to: {path}")
    print("Paste/update this row in data/MANIFEST.md:\n")
    print(
        f"| `{path.name}` | {grain} | {source_notebook} "
        f"| {date.today().isoformat()} | {len(df)} rows |"
    )