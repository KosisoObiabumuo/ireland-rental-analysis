-- Affordability by county: annual rent as a share of regional median earnings.
-- Rent is the latest-year average of the headline series, annualised (x12).
-- Earnings only exist at NUTS 3 region level and only up to 2024, so each county
-- maps to its region and the most recent earnings year is used as the divisor.

DROP VIEW IF EXISTS v_affordability;

CREATE VIEW v_affordability AS
WITH rent_year AS (
    SELECT max(year) AS y FROM rtb_rent
),
earn_year AS (
    SELECT max(year) AS y FROM earnings WHERE region <> 'State'
),
rent AS (
    SELECT county, round(avg(rent), 0) AS avg_monthly_rent
    FROM rtb_rent
    WHERE year = (SELECT y FROM rent_year)
      AND bedrooms = 'All bedrooms'
      AND property_type = 'All property types'
    GROUP BY county
)
SELECT
    r.county,
    cr.region,
    (SELECT y FROM rent_year)                                       AS rent_year,
    (SELECT y FROM earn_year)                                       AS earnings_year,
    r.avg_monthly_rent,
    round(r.avg_monthly_rent * 12, 0)                              AS annual_rent,
    e.median_earnings,
    round(r.avg_monthly_rent * 12 / e.median_earnings * 100, 1)   AS rent_pct_of_income
FROM rent r
JOIN county_region cr ON cr.county = r.county
JOIN earnings e ON e.region = cr.region AND e.year = (SELECT y FROM earn_year)
ORDER BY rent_pct_of_income DESC;
