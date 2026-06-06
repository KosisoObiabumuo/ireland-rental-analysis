-- Rent growth by county: first vs latest available quarter.
-- Uses the headline "All bedrooms / All property types" series so each county
-- is a single comparable rent figure per quarter. Not every county has data in
-- 2014Q1, so we take each county's own earliest and latest published quarter.

DROP VIEW IF EXISTS v_rent_growth;

CREATE VIEW v_rent_growth AS
WITH base AS (
    SELECT county, quarter, date, rent
    FROM rtb_rent
    WHERE bedrooms = 'All bedrooms'
      AND property_type = 'All property types'
),
endpoints AS (
    SELECT
        county,
        (array_agg(quarter ORDER BY date))[1]            AS first_quarter,
        (array_agg(rent    ORDER BY date))[1]            AS first_rent,
        (array_agg(quarter ORDER BY date DESC))[1]       AS last_quarter,
        (array_agg(rent    ORDER BY date DESC))[1]       AS last_rent,
        count(*)                                         AS n_quarters
    FROM base
    GROUP BY county
)
SELECT
    county,
    first_quarter,
    first_rent,
    last_quarter,
    last_rent,
    round(last_rent - first_rent, 2)                          AS rent_change,
    round((last_rent - first_rent) / first_rent * 100, 1)     AS pct_change,
    n_quarters
FROM endpoints
ORDER BY pct_change DESC;
