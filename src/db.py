import duckdb
from src.config import DATA_DB

def get_connection(read_only=False):
    return duckdb.connect(str(DATA_DB), read_only=read_only)