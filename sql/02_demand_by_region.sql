-- Aggregate population demand by US Census region
-- Uses CASE mapping of state_id -> region
SELECT
    region,
    COUNT(*)                          AS city_count,
    SUM(population)                   AS total_population,
    ROUND(AVG(population), 0)         AS avg_city_population,
    MAX(population)                   AS max_city_population,
    ROUND(SUM(population) * 100.0 /
          (SELECT SUM(population) FROM cities WHERE population > 0), 2)
                                      AS pct_national_population
FROM (
    SELECT
        population,
        CASE
            WHEN state_id IN ('CT','ME','MA','NH','NJ','NY','PA','RI','VT')
                THEN 'Northeast'
            WHEN state_id IN ('IL','IN','IA','KS','MI','MN','MO','NE','ND','OH','SD','WI')
                THEN 'Midwest'
            WHEN state_id IN ('AL','AR','DE','FL','GA','KY','LA','MD','MS','NC','OK','SC','TN','TX','VA','WV','DC')
                THEN 'South'
            WHEN state_id IN ('AK','AZ','CA','CO','HI','ID','MT','NV','NM','OR','UT','WA','WY')
                THEN 'West'
            ELSE 'Territory'
        END AS region
    FROM cities
    WHERE population IS NOT NULL AND population > 0
) AS regional
GROUP BY region
ORDER BY total_population DESC;
