# Data sources

This folder holds the raw and processed datasets used in the analysis. Raw files in `data/raw/` are gitignored because they're large. To reproduce the project, download them yourself using the notes below.

All three sources are free, public, and licensed for reuse under Ireland's Public Sector Information (PSI) terms.

---

## 1. RTB Rent Index

**File:** `raw/rtb_rent_index.csv`
**Source:** [data.cso.ie](https://data.cso.ie), table titled *RTB Average Monthly Rent Report (Quarterly)*
**Publisher:** Residential Tenancies Board (RTB), via the Central Statistics Office portal
**Retrieved:** 2 May 2026
**Coverage:** Q1 2014 to Q3 2025

Quarterly average rents reported on tenancies registered with the RTB. The portal lets you build a table by selecting dimensions, then export to CSV. For this project I selected:

- **Location:** all available (446 entries, including 26 counties plus cities and towns within them)
- **Property Type:** all (Detached, Semi-detached, Terrace, Apartment, Other flats, plus the "All property types" total)
- **Number of Bedrooms:** all (1 bed, 2 bed, 3 bed, 4+ bed, plus the "1 to 2", "1 to 3", "All bedrooms" aggregates)
- **Time:** Q1 2014 onwards, to fit the portal's 1 million cell export limit

The earlier history (back to Q4 2007) is available on the portal but the file gets too large with the location detail kept in.

**Columns:** STATISTIC Label, Quarter, Number of Bedrooms, Property Type, Location, UNIT, VALUE
**Rows:** 880,404
**Quirks:** about 73% of rows have a null `VALUE`. That's the small towns and granular bedroom-by-property splits where there aren't enough tenancy registrations in a given quarter to publish a number. The county-level totals are densely populated.

The original RTB site at [rtb.ie/data-insights/rtb-data-hub](https://rtb.ie/data-insights/rtb-data-hub/rtb-esri-rent-index-data-set/) only publishes single-quarter snapshot spreadsheets (Q3 2025 at the time I checked), which is why I went straight to the CSO portal for the historical series.

---

## 2. CSO Annual Earnings by NUTS 3 Region

**File:** `raw/cso_earnings.csv`
**Source:** [data.cso.ie](https://data.cso.ie), *Mean and Median Annual Earnings by NUTS 3 Region*
**Publisher:** Central Statistics Office
**Retrieved:** 2 May 2026
**Coverage:** 2011 to 2024

Annual earnings broken out by NUTS 3 region. The eight NUTS 3 regions are: Border, Midland, West, Dublin, Mid-East, Mid-West, South-East, South-West, plus a State (national) total.

CSO doesn't publish earnings at county level. Sample sizes per county are too small to release without breaching disclosure rules, so the rent-vs-earnings affordability analysis in this project maps each county to its parent NUTS 3 region and uses the regional median as the divisor.

**Columns:** Statistic Label, Year, Sex, NUTS 3 Regions, UNIT, VALUE
**Rows:** 756
**Quirks:** earnings ends at 2024 because the 2025 annual figure isn't published until well into 2026. Rent-to-earnings ratios for 2025 will be computed using 2024 earnings as the most recent available, with that limitation flagged in the writeup.

---

## 3. Residential Property Price Register

**File:** `raw/ppr.csv`
**Source:** [propertypriceregister.ie](https://www.propertypriceregister.ie/)
**Publisher:** Property Services Regulatory Authority
**Retrieved:** 2 May 2026
**Coverage:** 1 January 2010 to 24 April 2026

The PPR is a legally-mandated record of every residential property sale that goes through stamp duty in Ireland. This project uses it to cross-check rent trends against sale-price trends, and to characterise the housing stock at county level.

**Columns:** Date of Sale, Address, County, Eircode, Price, Not Full Market Price, VAT Exclusive, Description of Property, Property Size Description
**Rows:** 782,596
**Quirks worth knowing:**
- Encoded in **cp1252 / Windows-1252**, not UTF-8. Pandas needs `encoding='cp1252'` or it'll throw a UnicodeDecodeError. Address fields with fadas (á, é, í, ó, ú) and the Euro sign in the Price column are why.
- Eircodes are 70% null. The Eircode system rolled out in 2015 so older sales don't have one.
- Property Size Description is 93% null. It's only filled in for new builds, and only consistently from 2010 to about 2014.
- The Price column header has a Euro sign that displays as `?` or `?` in some terminals. The numeric values themselves are fine.
- Some rows have "Not Full Market Price" set to "Yes". These are typically family transfers, distressed sales, or intra-corporate moves and need to be filtered out for any market-rate analysis.

---

## Reproducing this folder

1. Make a free CSO Open Data account if the portal asks (it usually doesn't for public tables).
2. For each of the three files above, follow the source link and download the CSV with the dimensions listed in the bullet points.
3. Save each to `data/raw/` with the exact filename shown.
4. Run the cleaning notebook (`notebooks/02_clean.ipynb`) which produces the files in `data/processed/`.

If a file fails to load, the most common cause is the encoding for the PPR or a missed dimension on the CSO portal export. Check the column list in this file against your download.
