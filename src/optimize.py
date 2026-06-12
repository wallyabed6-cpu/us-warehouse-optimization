"""
P-median facility-location optimizer.

For each scenario k (number of warehouses), finds the k locations from the
75 demand nodes that minimize total population-weighted distance:

    minimize  sum_i  population_i * distance(i, nearest_facility)

Algorithm:
  1. Greedy initialization  — add facilities one at a time, each time picking
     the candidate that gives the greatest reduction in total cost.
  2. Local-search (swap)    — repeatedly try swapping each open facility with
     each closed candidate; keep any swap that improves total cost.
     Repeat until no improving swap exists (local optimum).

Outputs one JSON file per scenario to exports/.
"""
import json
import os
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
MATRIX_PATH = os.path.join(ROOT, "data", "distance_matrix.npy")
NODES_PATH = os.path.join(ROOT, "data", "nodes.json")
EXPORTS_DIR = os.path.join(ROOT, "exports")

SCENARIOS = [3, 4, 5, 6, 7, 8]   # warehouse counts to evaluate


# ---------------------------------------------------------------------------
# Cost helpers
# ---------------------------------------------------------------------------

def total_cost(dist_matrix, population, open_set):
    """Total population-weighted distance for a given set of open facilities."""
    sub = dist_matrix[:, list(open_set)]        # (N, k)
    nearest = sub.min(axis=1)                   # (N,)
    return float(np.dot(population, nearest))


def assignment(dist_matrix, open_set):
    """Return array: for each node, index into sorted(open_set) of its nearest facility."""
    sub = dist_matrix[:, sorted(open_set)]
    return np.argmin(sub, axis=1)


# ---------------------------------------------------------------------------
# Greedy initialisation
# ---------------------------------------------------------------------------

def greedy_init(dist_matrix, population, k):
    n = dist_matrix.shape[0]
    open_set = set()
    # Best single facility = weighted median proxy: minimise total weighted dist
    costs = [np.dot(population, dist_matrix[:, j]) for j in range(n)]
    open_set.add(int(np.argmin(costs)))

    while len(open_set) < k:
        best_gain, best_j = -1, -1
        current_cost = total_cost(dist_matrix, population, open_set)
        for j in range(n):
            if j in open_set:
                continue
            candidate = open_set | {j}
            c = total_cost(dist_matrix, population, candidate)
            gain = current_cost - c
            if gain > best_gain:
                best_gain, best_j = gain, j
        open_set.add(best_j)

    return open_set


# ---------------------------------------------------------------------------
# Local-search (swap)
# ---------------------------------------------------------------------------

def local_search(dist_matrix, population, open_set):
    n = dist_matrix.shape[0]
    improved = True
    while improved:
        improved = False
        best_cost = total_cost(dist_matrix, population, open_set)
        found = False
        for fac in sorted(open_set):
            if found:
                break
            for cand in range(n):
                if cand in open_set:
                    continue
                new_set = (open_set - {fac}) | {cand}
                c = total_cost(dist_matrix, population, new_set)
                if c < best_cost - 1e-6:
                    best_cost = c
                    open_set = new_set
                    improved = True
                    found = True
                    break
    return open_set


# ---------------------------------------------------------------------------
# Run one scenario
# ---------------------------------------------------------------------------

def run_scenario(k, dist_matrix, population, nodes):
    open_set = greedy_init(dist_matrix, population, k)
    open_set = local_search(dist_matrix, population, open_set)

    cost = total_cost(dist_matrix, population, open_set)
    assign = assignment(dist_matrix, open_set)

    open_list = sorted(open_set)
    fac_nodes = [nodes[i] for i in open_list]

    # Build cluster summary
    clusters = []
    for rank, fac_idx in enumerate(open_list):
        served = [i for i, a in enumerate(assign) if open_list[a] == fac_idx]
        cluster_pop = int(sum(nodes[i]["population"] for i in served))
        avg_dist = float(np.dot(
            [nodes[i]["population"] for i in served],
            [dist_matrix[i, fac_idx] for i in served]
        ) / cluster_pop) if cluster_pop else 0.0

        clusters.append({
            "facility": {
                "city": nodes[fac_idx]["city"],
                "state_id": nodes[fac_idx]["state_id"],
                "lat": nodes[fac_idx]["lat"],
                "lng": nodes[fac_idx]["lng"],
                "population": nodes[fac_idx]["population"],
            },
            "served_cities": len(served),
            "served_population": cluster_pop,
            "avg_weighted_distance_mi": round(avg_dist, 1),
            "demand_nodes": [
                {
                    "city": nodes[i]["city"],
                    "state_id": nodes[i]["state_id"],
                    "lat": nodes[i]["lat"],
                    "lng": nodes[i]["lng"],
                    "population": nodes[i]["population"],
                    "distance_to_facility_mi": round(float(dist_matrix[i, fac_idx]), 1),
                }
                for i in sorted(served, key=lambda x: -nodes[x]["population"])
            ],
        })

    total_pop = int(sum(n["population"] for n in nodes))
    return {
        "scenario": f"{k}-warehouse",
        "k": k,
        "total_weighted_distance_mi": round(cost, 0),
        "avg_distance_per_capita_mi": round(cost / total_pop, 2),
        "total_demand_population": total_pop,
        "warehouses": clusters,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dist_matrix = np.load(MATRIX_PATH)
    with open(NODES_PATH) as f:
        nodes = json.load(f)
    population = np.array([n["population"] for n in nodes], dtype=np.float64)

    os.makedirs(EXPORTS_DIR, exist_ok=True)

    all_summaries = []

    for k in SCENARIOS:
        print(f"\nOptimizing k={k} warehouses...", end=" ", flush=True)
        result = run_scenario(k, dist_matrix, population, nodes)

        out_path = os.path.join(EXPORTS_DIR, f"scenario_{k}wh.json")
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)

        cost = result["total_weighted_distance_mi"]
        avg = result["avg_distance_per_capita_mi"]
        print(f"done  |  total weighted dist: {cost:,.0f} mi  |  avg/capita: {avg} mi")

        print(f"  Optimal warehouse locations:")
        for c in result["warehouses"]:
            fac = c["facility"]
            print(f"    {fac['city']}, {fac['state_id']}  "
                  f"({c['served_cities']} cities, "
                  f"pop {c['served_population']:,}, "
                  f"avg dist {c['avg_weighted_distance_mi']} mi)")

        all_summaries.append({
            "k": k,
            "scenario": result["scenario"],
            "total_weighted_distance_mi": cost,
            "avg_distance_per_capita_mi": avg,
            "warehouses": [
                f"{c['facility']['city']}, {c['facility']['state_id']}"
                for c in result["warehouses"]
            ],
        })

    # Combined summary file for dashboard
    summary_path = os.path.join(EXPORTS_DIR, "scenarios_summary.json")
    with open(summary_path, "w") as f:
        json.dump(all_summaries, f, indent=2)
    print(f"\nSummary saved -> {summary_path}")

    # Print improvement table
    print("\n-- Cost vs. Number of Warehouses ------------------------------")
    print(f"  {'k':>3}  {'Total Wtd Dist (mi)':>22}  {'Avg/Capita (mi)':>18}  {'Savings vs k-1':>16}")
    print(f"  {'---':>3}  {'----------------------':>22}  {'------------------':>18}  {'----------------':>16}")
    prev = None
    for s in all_summaries:
        savings = f"{(prev - s['total_weighted_distance_mi']) / prev * 100:.1f}%" if prev else "—"
        print(f"  {s['k']:>3}  {s['total_weighted_distance_mi']:>22,.0f}  "
              f"{s['avg_distance_per_capita_mi']:>18.2f}  {savings:>16}")
        prev = s["total_weighted_distance_mi"]


if __name__ == "__main__":
    main()
