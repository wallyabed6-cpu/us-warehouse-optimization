"""
Build the haversine distance matrix for the 75 demand nodes.

Demand-node selection (applied here, not in the population-only SQL):
  1. Contiguous US only -- exclude offshore states/territories (AK, HI, PR, ...)
     because this is a road-freight model and haversine to an offshore city
     is meaningless.
  2. Metro de-duplication -- walk candidate cities largest-to-smallest and skip
     any city within DEDUP_RADIUS_MI of an already-accepted larger city. The raw
     simplemaps dataset assigns metro-level population to a principal city AND
     lists sub-places separately (e.g. New York's boroughs, Fort Worth vs Dallas),
     which double-counts demand. This step collapses each urban agglomeration to
     a single node carrying the principal city's population.
  3. Keep the top 75 survivors by population.

Outputs:
  data/distance_matrix.npy   -- numpy float32 array (75x75), distances in miles
  data/nodes.json            -- ordered list of demand node metadata
"""
import json
import math
import sqlite3
import os
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(ROOT, "data", "warehouse.db")
MATRIX_PATH = os.path.join(ROOT, "data", "distance_matrix.npy")
NODES_PATH = os.path.join(ROOT, "data", "nodes.json")

EARTH_RADIUS_MI = 3958.8
DEDUP_RADIUS_MI = 35       # cities within this radius of a larger one are absorbed
N_NODES = 75               # final demand-node count
CANDIDATE_POOL = 200       # how many top cities to pull before de-duplicating

# Non-contiguous states / territories excluded from the road-freight model
OFFSHORE = {"AK", "HI", "PR", "GU", "VI", "MP", "AS"}


def haversine(lat1, lng1, lat2, lng2):
    """Great-circle distance in miles between two lat/lng points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(a))


def load_candidates(conn):
    """Top CONUS cities by population, before metro de-duplication."""
    placeholders = ",".join("?" for _ in OFFSHORE)
    cur = conn.execute(f"""
        SELECT city, state_id, state_name, lat, lng, population
        FROM cities
        WHERE population > 0
          AND lat IS NOT NULL AND lng IS NOT NULL
          AND state_id NOT IN ({placeholders})
        ORDER BY population DESC
        LIMIT ?
    """, (*OFFSHORE, CANDIDATE_POOL))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def dedup_metros(candidates):
    """Greedy proximity de-dup: skip cities within DEDUP_RADIUS_MI of a larger
    accepted city. Candidates must already be sorted by population descending."""
    accepted, absorbed = [], []
    for c in candidates:
        parent = next(
            (a for a in accepted
             if haversine(c["lat"], c["lng"], a["lat"], a["lng"]) < DEDUP_RADIUS_MI),
            None,
        )
        if parent is None:
            accepted.append(c)
        else:
            absorbed.append((c, parent))
        if len(accepted) >= N_NODES:
            break
    return accepted, absorbed


def select_nodes(conn):
    candidates = load_candidates(conn)
    accepted, absorbed = dedup_metros(candidates)

    print(f"Candidate pool (CONUS, top {CANDIDATE_POOL} by pop): {len(candidates)}")
    if absorbed:
        print(f"Absorbed {len(absorbed)} sub-metro duplicate(s):")
        for c, parent in absorbed:
            print(f"  - {c['city']}, {c['state_id']} "
                  f"({c['population']:,}) -> {parent['city']}, {parent['state_id']}")
    print(f"Final demand nodes: {len(accepted)}\n")
    return accepted


def build_matrix(nodes):
    n = len(nodes)
    mat = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine(nodes[i]["lat"], nodes[i]["lng"],
                          nodes[j]["lat"], nodes[j]["lng"])
            mat[i, j] = d
            mat[j, i] = d
    return mat


def main():
    conn = sqlite3.connect(DB_PATH)
    nodes = select_nodes(conn)
    conn.close()

    mat = build_matrix(nodes)

    np.save(MATRIX_PATH, mat)
    print(f"Distance matrix saved  -> {MATRIX_PATH}  shape={mat.shape}")

    # Annotate nodes with their index for downstream use
    for i, node in enumerate(nodes):
        node["idx"] = i

    with open(NODES_PATH, "w") as f:
        json.dump(nodes, f, indent=2)
    print(f"Node metadata saved    -> {NODES_PATH}")

    # Quick sanity stats
    upper = mat[np.triu_indices(len(nodes), k=1)]
    print(f"\nDistance matrix stats (miles):")
    print(f"  min   : {upper.min():.1f}")
    print(f"  max   : {upper.max():.1f}")
    print(f"  mean  : {upper.mean():.1f}")
    print(f"  median: {np.median(upper):.1f}")

    # Nearest-neighbour check
    print("\nNearest neighbours (top 5 pairs):")
    pairs = sorted(
        ((mat[i, j], nodes[i]["city"], nodes[j]["city"])
         for i in range(len(nodes)) for j in range(i + 1, len(nodes))),
        key=lambda x: x[0]
    )[:5]
    for dist, a, b in pairs:
        print(f"  {a} <-> {b}: {dist:.1f} mi")


if __name__ == "__main__":
    main()
