# US Warehouse Network Optimization

A facility-location model that identifies the optimal placement of distribution
centers across the contiguous United States to minimize total population-weighted
shipping distance. Includes an interactive executive dashboard for scenario analysis.

## Project Structure

```
data/        Raw input data + generated SQLite DB and distance matrix
sql/         SQL scripts — filtering, aggregation, demand summary
src/         Python pipeline — data loading, distance matrix, optimization
exports/     JSON scenario outputs consumed by the dashboard
dashboard/   React executive dashboard (Vite + Leaflet + Chart.js)
```

## Stack

- **SQL** (SQLite) — population filtering and regional demand aggregation
- **Python** — haversine distance matrix, p-median facility-location optimizer
- **React + Leaflet + Chart.js** — interactive scenario dashboard

## Pipeline

```
python src/load_data.py    # CSV -> SQLite, run the three SQL reports
python src/distance.py     # select 75 demand nodes, build distance matrix
python src/optimize.py     # solve k = 3..8 warehouses, write exports/*.json
```

## Methodology

**Demand proxy.** Each demand node is a major US city; its population is used as a
proxy for shipping demand. Total cost is the population-weighted sum of each city's
distance to its nearest warehouse.

**Demand-node selection.** From the 31k-city dataset the model uses 75 nodes,
chosen in three steps:
1. **Contiguous US only.** Offshore states/territories (AK, HI, PR, …) are excluded
   — this is a road-freight model, so great-circle distance to an island metro is
   not meaningful.
2. **Metro de-duplication.** The raw simplemaps dataset assigns *metro-level*
   population to a principal city while also listing sub-places separately
   (e.g. New York's boroughs; Fort Worth alongside Dallas). Counting both
   double-counts demand. The pipeline absorbs any city within **35 miles** of a
   larger already-accepted city, collapsing each urban agglomeration to one node.
   This removed 11 duplicates (the 4 NYC boroughs, Fort Worth, Mesa, Ogden, and
   others), which meaningfully rebalanced the optimal network.
3. **Top 75 survivors** by population.

**Optimizer.** A p-median solver: greedy initialization (add the facility that most
reduces total cost) followed by swap-based local search (exchange open/closed
facilities until no improving swap exists).

## Known limitations

These are simplifying assumptions, stated plainly:

- **Straight-line distance.** Haversine underestimates real freight distance;
  road miles run roughly 1.2–1.4× longer. Relative comparisons between scenarios
  remain valid.
- **No capacity constraints.** Real distribution centers have throughput limits;
  the p-median model assigns each city to its nearest open facility regardless of
  facility load.
- **Local optimum.** Greedy + local search is near-optimal for this problem size
  but is not guaranteed to find the global optimum.
- **Population ≠ shipping volume.** Population is a stand-in for demand; actual
  e-commerce volume varies by region and demographics.

## Key result

The cost-vs-network-size curve shows an **elbow at k = 5** — adding the 5th
warehouse delivers the largest marginal savings (~22%), after which returns
diminish. Five DCs (New York, Los Angeles, Chicago, Dallas, Orlando) cover the
national demand efficiently.

## Data Source

[simplemaps US Cities](https://simplemaps.com/data/us-cities) (Basic v1.93).
Place `uscities.csv` in `data/`. Columns used: `city, state_id, state_name, lat, lng, population`.
