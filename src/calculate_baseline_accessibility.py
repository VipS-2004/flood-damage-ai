from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd


GRAPH_PATH = "data/processed/osm_20260727/road_network_metric.graphml"
SETTLEMENTS_PATH = "data/processed/osm_20260727/settlements_connected.parquet"
HOSPITALS_PATH = "data/processed/osm_20260727/hospitals_connected.parquet"

OUTPUT_PATH = Path(
    "data/processed/osm_20260727/baseline_accessibility.parquet"
)


print("Loading metric road graph...")

graph = nx.read_graphml(GRAPH_PATH)

print(f"Graph nodes: {graph.number_of_nodes()}")
print(f"Graph edges: {graph.number_of_edges()}")


print("Loading settlements...")

settlements = gpd.read_parquet(SETTLEMENTS_PATH)

print(f"Settlements: {len(settlements)}")


print("Loading hospitals...")

hospitals = gpd.read_parquet(HOSPITALS_PATH)

print(f"Hospitals: {len(hospitals)}")


hospital_nodes = hospitals["node"].dropna().astype(str).tolist()

if not hospital_nodes:
    raise RuntimeError("No hospital road nodes found.")


print("\nHospital road nodes:")

for node in hospital_nodes:
    print(f"  {node}")


results = []


for _, settlement in settlements.iterrows():

    settlement_node = str(settlement["node"])

    name = settlement.get("name")
    name_en = settlement.get("name_en")
    place = settlement.get("place")

    display_name = name_en or name or f"OSM {settlement['osm_id']}"

    best_distance = None
    best_hospital_node = None

    for hospital_node in hospital_nodes:

        try:
            distance_m = nx.shortest_path_length(
                graph,
                source=settlement_node,
                target=hospital_node,
                weight="length_m",
            )

        except nx.NetworkXNoPath:
            continue

        if best_distance is None or distance_m < best_distance:
            best_distance = distance_m
            best_hospital_node = hospital_node

    if best_distance is None:

        results.append({
            "osm_id": settlement["osm_id"],
            "name": name,
            "name_en": name_en,
            "display_name": display_name,
            "place": place,
            "settlement_node": settlement_node,
            "nearest_hospital_node": None,
            "baseline_distance_m": None,
            "baseline_distance_km": None,
            "baseline_accessible": False,
        })

        continue

    results.append({
        "osm_id": settlement["osm_id"],
        "name": name,
        "name_en": name_en,
        "display_name": display_name,
        "place": place,
        "settlement_node": settlement_node,
        "nearest_hospital_node": best_hospital_node,
        "baseline_distance_m": float(best_distance),
        "baseline_distance_km": float(best_distance) / 1000,
        "baseline_accessible": True,
    })


results_df = pd.DataFrame(results)


print("\nBaseline accessibility results:")

print(
    results_df[
        [
            "display_name",
            "place",
            "baseline_distance_km",
            "baseline_accessible",
        ]
    ].sort_values(
        "baseline_distance_km",
        na_position="last",
    ).to_string(index=False)
)


print("\nAccessibility summary:")

print(
    f"Total settlements: {len(results_df)}"
)

print(
    f"Reachable settlements: "
    f"{results_df['baseline_accessible'].sum()}"
)

print(
    f"Unreachable settlements: "
    f"{(~results_df['baseline_accessible']).sum()}"
)


reachable = results_df[
    results_df["baseline_accessible"]
]

if len(reachable) > 0:

    print(
        f"Minimum distance: "
        f"{reachable['baseline_distance_km'].min():.2f} km"
    )

    print(
        f"Median distance: "
        f"{reachable['baseline_distance_km'].median():.2f} km"
    )

    print(
        f"Maximum distance: "
        f"{reachable['baseline_distance_km'].max():.2f} km"
    )


results_df.to_parquet(
    OUTPUT_PATH,
    index=False,
)

print(f"\nSaved: {OUTPUT_PATH}")
print("Done.")