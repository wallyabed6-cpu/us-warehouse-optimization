-- Dataset summary statistics
SELECT
    COUNT(*)                                AS total_cities,
    SUM(population)                         AS total_us_population,
    ROUND(AVG(population), 0)               AS mean_population,
    MIN(population)                         AS min_population,
    MAX(population)                         AS max_population,
    COUNT(DISTINCT state_id)                AS states_covered,

    -- Concentration: what % of pop lives in top 10 / top 75 cities
    ROUND(
        (SELECT SUM(population) FROM (
            SELECT population FROM cities
            WHERE population > 0
            ORDER BY population DESC LIMIT 10
        )) * 100.0 / SUM(population), 2
    )                                       AS top10_pct_of_total,

    ROUND(
        (SELECT SUM(population) FROM (
            SELECT population FROM cities
            WHERE population > 0
            ORDER BY population DESC LIMIT 75
        )) * 100.0 / SUM(population), 2
    )                                       AS top75_pct_of_total

FROM cities
WHERE population IS NOT NULL AND population > 0;


-- Per-state breakdown
SELECT
    state_id,
    state_name,
    COUNT(*)                        AS city_count,
    SUM(population)                 AS state_population,
    MAX(population)                 AS largest_city_pop,
    (SELECT city FROM cities c2
     WHERE c2.state_id = c.state_id
     ORDER BY c2.population DESC LIMIT 1) AS largest_city
FROM cities c
WHERE population IS NOT NULL AND population > 0
GROUP BY state_id, state_name
ORDER BY state_population DESC
LIMIT 20;
