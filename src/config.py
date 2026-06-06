from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_GENERATED = PROJECT_ROOT / "data" / "generated"
DATA_DB = PROJECT_ROOT / "data" / "claims.duckdb"