"""Load the Olist CSVs in data/ into olist.duckdb. Run once: python build_db.py"""
import glob
import os

import duckdb

SKIP = {"geolocation"}  # 1M rows, not needed for the questions we ask

con = duckdb.connect("olist.duckdb")
paths = sorted(glob.glob("data/*.csv"))
if not paths:
    raise SystemExit("No CSVs found. Unzip the Kaggle Olist download into data/ first.")

for path in paths:
    name = os.path.basename(path).removesuffix(".csv")
    name = name.removeprefix("olist_").removesuffix("_dataset")
    if name in SKIP:
        continue
    con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto('{path}')")
    rows = con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
    print(f"{name}: {rows:,} rows")
