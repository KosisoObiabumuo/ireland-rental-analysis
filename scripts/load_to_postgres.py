"""Load the processed CSVs in data/processed/ into a PostgreSQL database.

Run after notebooks/02_clean.ipynb has produced the processed files:

    uv run python scripts/load_to_postgres.py

Connection settings are read from environment variables so no credentials live
in the repo. Defaults target a local install:

    PGHOST      (default: localhost)
    PGPORT      (default: 5432)
    PGUSER      (default: postgres)
    PGDATABASE  (default: ireland_rental)
    PGPASSWORD  (required, no default)

Each table is dropped and recreated so the script is safe to re-run.
"""

import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import (
    Date,
    Integer,
    Numeric,
    String,
    create_engine,
    text,
)
from sqlalchemy.engine import URL

PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"

# table name -> (csv file, column dtypes for the SQL schema)
TABLES = {
    "county_region": (
        "county_region.csv",
        {"county": String(40), "region": String(40)},
    ),
    "earnings": (
        "earnings.csv",
        {
            "region": String(40),
            "year": Integer(),
            "mean_earnings": Numeric(10, 2),
            "median_earnings": Numeric(10, 2),
        },
    ),
    "rtb_rent": (
        "rtb_rent.csv",
        {
            "county": String(40),
            "quarter": String(8),
            "date": Date(),
            "year": Integer(),
            "bedrooms": String(20),
            "property_type": String(30),
            "rent": Numeric(10, 2),
        },
    ),
    "ppr_sales": (
        "ppr_sales.csv",
        {
            "date": Date(),
            "year": Integer(),
            "county": String(40),
            "price": Numeric(14, 2),
            "description": String(60),
        },
    ),
}

# indexes that speed up the joins/filters used in the analysis
INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_rtb_county_year ON rtb_rent (county, year)",
    "CREATE INDEX IF NOT EXISTS ix_ppr_county_year ON ppr_sales (county, year)",
    "CREATE INDEX IF NOT EXISTS ix_earnings_region_year ON earnings (region, year)",
]

# columns to parse as dates when reading each CSV back in
DATE_COLS = {"rtb_rent": ["date"], "ppr_sales": ["date"]}


def make_engine():
    password = os.environ.get("PGPASSWORD")
    if not password:
        sys.exit(
            "PGPASSWORD is not set. Set it (e.g. setx PGPASSWORD \"...\") and "
            "open a new terminal, then re-run."
        )
    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ.get("PGUSER", "postgres"),
        password=password,
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        database=os.environ.get("PGDATABASE", "ireland_rental"),
    )
    return create_engine(url)


def main():
    engine = make_engine()

    for table, (filename, dtypes) in TABLES.items():
        path = PROCESSED / filename
        if not path.exists():
            sys.exit(f"Missing {path}. Run the cleaning notebook first.")

        df = pd.read_csv(path, parse_dates=DATE_COLS.get(table))
        df.to_sql(
            table,
            engine,
            if_exists="replace",
            index=False,
            dtype=dtypes,
            chunksize=5000,
            method="multi",
        )
        print(f"loaded {table:14s} {len(df):>9,} rows, {len(df.columns)} cols")

    with engine.begin() as conn:
        for stmt in INDEXES:
            conn.execute(text(stmt))
    print(f"created {len(INDEXES)} indexes")

    # quick confirmation of row counts straight from the database
    with engine.connect() as conn:
        print("\nrow counts in database:")
        for table in TABLES:
            n = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
            print(f"  {table:14s} {n:>9,}")


if __name__ == "__main__":
    main()
