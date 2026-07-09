"""Export the analysis outputs to CSVs that Tableau Public can read.

Tableau Public (the free edition) cannot connect to a local PostgreSQL server;
it only reads file-based sources. This script pulls the three analysis views
plus the headline rent time series out of the database and writes them to
data/tableau/ so the dashboard can be built on flat files.

Run after the views exist (see sql/) and the database is loaded:

    uv run python scripts/export_for_tableau.py

Connection settings are read from the same PG* environment variables the load
script uses, so no credentials live in the repo.
"""

import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

OUT = Path(__file__).resolve().parent.parent / "data" / "tableau"

# output file -> query. The three views feed the county/bedroom charts; the
# time series feeds an interactive rent-over-time trend by county.
EXPORTS = {
    "rent_growth.csv": "SELECT * FROM v_rent_growth ORDER BY pct_change DESC",
    "affordability.csv": "SELECT * FROM v_affordability ORDER BY rent_pct_of_income DESC",
    "bedroom_premium.csv": "SELECT * FROM v_bedroom_premium ORDER BY bed_order",
    "rent_timeseries.csv": (
        "SELECT county, quarter, date, year, rent "
        "FROM rtb_rent "
        "WHERE bedrooms = 'All bedrooms' "
        "AND property_type = 'All property types' "
        "ORDER BY county, date"
    ),
}


def get_engine():
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
    OUT.mkdir(parents=True, exist_ok=True)
    engine = get_engine()

    with engine.connect() as conn:
        for filename, query in EXPORTS.items():
            df = pd.read_sql(text(query), conn)
            df.to_csv(OUT / filename, index=False)
            print(f"wrote {filename:22s} {len(df):>6,} rows, {len(df.columns)} cols")

    print(f"\nexports written to {OUT}")


if __name__ == "__main__":
    main()
