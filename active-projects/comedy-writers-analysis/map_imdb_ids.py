# map_imdb_ids.py
import duckdb, pandas as pd
from rapidfuzz import fuzz
from tqdm import tqdm

WRITER_CSV  = "comedy_writers_with_scores.csv"
IMDB_TSV_GZ = "data/name.basics.tsv.gz"      # change if stored elsewhere

# -----------------------------------------------------------
# 1) load writer list
# -----------------------------------------------------------
writers = pd.read_csv(WRITER_CSV)[["Writer Name"]]
writers["key"] = writers["Writer Name"].str.lower().str.strip()

# -----------------------------------------------------------
# 2) spin up DuckDB and ingest IMDb dump
# -----------------------------------------------------------
con = duckdb.connect()          # in-memory DB, no file needed

con.execute(
    """
    CREATE OR REPLACE TABLE imdb_names AS
    SELECT
        nconst,
        lower(trim(primaryName)) AS key,
        primaryName,
        birthYear
    FROM read_csv_auto(
        ?,                      -- parameter placeholder
        delim = '\t',
        header = TRUE,
        compression = 'gzip'
    );
    """,
    [IMDB_TSV_GZ]               # param list — keeps SQL readable
)

con.execute(
    "CREATE INDEX IF NOT EXISTS idx_imdb_key ON imdb_names(key);"
)

# -----------------------------------------------------------
# 3) exact-then-fuzzy matching helper
# -----------------------------------------------------------
def match(name_key: str) -> str | None:
    row = con.execute(
        "SELECT nconst FROM imdb_names WHERE key = ? LIMIT 1;",
        [name_key]
    ).fetchone()
    if row:                       # perfect match
        return row[0]

    # fuzzy fallback (grab a handful of similar names)
    cand = con.execute(
        """
        SELECT nconst, primaryName
        FROM imdb_names
        WHERE key LIKE ? LIMIT 5;
        """,
        [name_key[:4] + '%']
    ).fetchall()

    if not cand:
        return None
    best = max(cand, key=lambda r: fuzz.ratio(r[1].lower(), name_key))
    return best[0] if fuzz.ratio(best[1].lower(), name_key) >= 85 else None

# -----------------------------------------------------------
# 4) run the lookup with a progress bar
# -----------------------------------------------------------
tqdm.pandas(desc="Matching IMDb IDs")
writers["imdb_nm_id"] = writers["key"].progress_apply(match)

# -----------------------------------------------------------
# 5) merge back to the original CSV
# -----------------------------------------------------------
full = pd.read_csv(WRITER_CSV)
full["imdb_nm_id"] = writers["imdb_nm_id"]
full.to_csv("comedy_writers_with_ids.csv", index=False)

hits = full["imdb_nm_id"].notna().sum()
print(f"✓ Found IMDb IDs for {hits}/{len(full)} writers "
      f"({hits/len(full):.1%} coverage)")
