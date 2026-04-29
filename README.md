# Ireland Rental Market Analysis (2014 to 2025)

How rents in Ireland have moved over the last decade, broken down by county, dwelling type, and bedroom count, with a look at where rent is hardest to afford relative to local wages.

**Tableau Public dashboard:** _coming once published (Step 7.5)_

## The question

Where in Ireland has rent grown fastest, where is it most unaffordable compared to what people actually earn, and how much extra does each additional bedroom cost?

## Key findings

_Filling these in once the analysis is done. Each one will cite a number with the year range it covers._

1. TBD
2. TBD
3. TBD

## Data sources

All public, no scraping.

* **RTB Rent Index** from the Residential Tenancies Board. Quarterly average rents by county, dwelling type, and bedroom count.
* **CSO Ireland**, earnings data used to build the affordability ratio (rent over local income).
* **Property Price Register**, residential sale prices since 2010.

Source URLs and the date each file was downloaded live in `data/README.md`.

## Tools used

* Python (pandas) for cleaning and analysis
* PostgreSQL for the SQL layer
* Tableau Public for the dashboard
* Jupyter for the analysis notebooks

## How to reproduce

```bash
git clone https://github.com/KosisoObiabumuo/ireland-rental-analysis.git
cd ireland-rental-analysis
uv sync
uv run jupyter lab
```

To rebuild the database tables, drop the source files into `data/raw/` (see `data/README.md` for what goes where), then run `uv run python scripts/load_to_postgres.py`.

## Limitations

A few honest caveats up front.

* The RTB index covers registered tenancies only, so the more informal end of the rental market (rent a room, short term lets) is not in the data.
* County level averages hide a lot of within-county variation. Dublin city centre and the outer suburbs are very different markets.
* CSO earnings data is reported by region, not always by exact county, so the affordability ratio is approximate.
* More caveats will go here as the analysis surfaces specific issues.

## About me

I am Kosiso, a third year student in Ireland. This is a portfolio project I built after finishing the Google Data Analytics certificate on Coursera. Open to data analytics internships for summer 2026.

LinkedIn: _add link_
