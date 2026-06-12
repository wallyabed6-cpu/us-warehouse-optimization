-- Candidate demand nodes for the facility-location model.
--
-- This SQL handles the population + geography filter only. Two further steps are
-- applied in the Python prep layer (src/distance.py), because they require
-- great-circle distance math that SQLite does not express cleanly:
--   1. Metro de-duplication: the raw simplemaps data assigns metro-level
--      population to a principal city AND lists sub-places separately
--      (e.g. New York's boroughs, Fort Worth alongside Dallas). Those are
--      collapsed by absorbing any city within 35 mi of a larger accepted city.
--   2. Final cut to the top 75 survivors.
--
-- Offshore states/territories are excluded here: this is a road-freight model,
-- so haversine distance to an island metro (San Juan, Honolulu, Anchorage) is
-- not meaningful.

SELECT
    city,
    state_id,
    state_name,
    ROUND(lat, 4)        AS lat,
    ROUND(lng, 4)        AS lng,
    population,
    RANK() OVER (ORDER BY population DESC) AS demand_rank
FROM cities
WHERE population IS NOT NULL
  AND population > 0
  AND state_id NOT IN ('AK','HI','PR','GU','VI','MP','AS')   -- contiguous US only
ORDER BY population DESC
LIMIT 200;   -- candidate pool; de-dup + top-75 cut happens in src/distance.py
