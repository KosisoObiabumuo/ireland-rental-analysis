-- Bedroom premium: how much each extra bedroom adds to rent, nationally,
-- in the latest year. Averages the per-county published rents for each bedroom
-- size (All property types), then uses a window function to get the step-up
-- cost and percentage uplift from the next-smaller size.

DROP VIEW IF EXISTS v_bedroom_premium;

CREATE VIEW v_bedroom_premium AS
WITH latest AS (
    SELECT max(year) AS y FROM rtb_rent
),
by_size AS (
    SELECT
        bedrooms,
        CASE bedrooms
            WHEN 'One bed'       THEN 1
            WHEN 'Two bed'       THEN 2
            WHEN 'Three bed'     THEN 3
            WHEN 'Four plus bed' THEN 4
        END                              AS bed_order,
        round(avg(rent), 0)              AS avg_rent
    FROM rtb_rent
    WHERE year = (SELECT y FROM latest)
      AND property_type = 'All property types'
      AND bedrooms IN ('One bed', 'Two bed', 'Three bed', 'Four plus bed')
    GROUP BY bedrooms
)
SELECT
    bedrooms,
    bed_order,
    avg_rent,
    avg_rent - lag(avg_rent) OVER (ORDER BY bed_order)                        AS extra_vs_smaller,
    round(
        (avg_rent - lag(avg_rent) OVER (ORDER BY bed_order))
        / lag(avg_rent) OVER (ORDER BY bed_order) * 100, 1
    )                                                                          AS pct_uplift
FROM by_size
ORDER BY bed_order;
