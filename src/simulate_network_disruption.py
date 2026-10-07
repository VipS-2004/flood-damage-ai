from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

GRAPH_PATH = BASE_DIR / "data/processed/osm_20260727/road_network_metric.graphml"
AFFECTED_ROADS_PATH = BASE_DIR / "data/processed/osm_20260727/potentially_affected_roads.parquet"
SETTLEMENTS_PATH = BASE_DIR / "data/processed/osm_20260727/settlements_connected.parquet"
HOSPITALS_PATH = BASE_DIR / "data/processed/osm_20260727/hospitals_connected.parquet"
BASELINE_PATH = BASE_DIR / "data/processed/osm_20260727/baseline_accessibility.parquet"

OUTPUT_DIR = BASE_DIR / "data/processed/osm_20260727"
RESULT_PATH = OUTPUT_DIR / "network_disruption_results.parquet"
DISRUPTED_GRAPH_PATH = OUTPUT_DIR / "road_network_disrupted.graphml"


def normalize_graph(graph):
    for u, v, data in graph.edges(data=True):
        data["length_m"] = float(data["length_m"])
        data["osm_id"] = str(data["osm_id"])

    return graph


def get_nearest_hospital(graph, settlement_node, hospital_nodes):
    best_distance = None
    best_hospital = None

    for hospital_name, hospital_node in hospital_nodes:
        try:
            distance_m = nx.shortest_path_length(
                graph,
                source=settlement_node,
                target=hospital_node,
                weight="length_m",
            )
        except nx.NetworkXNoPath:
            continue
        except nx.NodeNotFound:
            continue

        if best_distance is None or distance_m < best_distance:
            best_distance = distance_m
            best_hospital = hospital_name

    if best_distance is None:
        return None, None

    return best_distance, best_hospital


def main():
    print("Loading road network...")
    graph = nx.read_graphml(GRAPH_PATH)
    graph = normalize_graph(graph)

    print(
        f"Original graph: "
        f"{graph.number_of_nodes():,} nodes, "
        f"{graph.number_of_edges():,} edges"
    )

    print("Loading potentially affected roads...")
    affected_roads = gpd.read_parquet(AFFECTED_ROADS_PATH)

    affected_ids = set(
        affected_roads["osm_id"]
        .astype(str)
        .tolist()
    )

    print(
        f"Potentially affected OSM road features: "
        f"{len(affected_ids)}"
    )

    disrupted_graph = graph.copy()

    edges_to_remove = []

    for u, v, data in disrupted_graph.edges(data=True):
        osm_id = str(data.get("osm_id", ""))

        if osm_id in affected_ids:
            edges_to_remove.append((u, v))

    disrupted_graph.remove_edges_from(edges_to_remove)

    print(f"Removed graph edges: {len(edges_to_remove):,}")

    print(
        f"Disrupted graph: "
        f"{disrupted_graph.number_of_nodes():,} nodes, "
        f"{disrupted_graph.number_of_edges():,} edges"
    )

    nx.write_graphml(
        disrupted_graph,
        DISRUPTED_GRAPH_PATH,
    )

    print("Loading settlements...")
    settlements = gpd.read_parquet(SETTLEMENTS_PATH)

    print("Loading hospitals...")
    hospitals = gpd.read_parquet(HOSPITALS_PATH)

    print("Loading baseline accessibility...")
    baseline = pd.read_parquet(BASELINE_PATH)

    settlements["osm_id"] = settlements["osm_id"].astype(str)
    hospitals["osm_id"] = hospitals["osm_id"].astype(str)
    baseline["osm_id"] = baseline["osm_id"].astype(str)

    hospital_nodes = []

    for _, row in hospitals.iterrows():
        hospital_name = row.get("name")

        if pd.isna(hospital_name):
            hospital_name = "Unnamed hospital"

        hospital_node = str(row["node"])

        hospital_nodes.append(
            (str(hospital_name), hospital_node)
        )

    results = []

    for _, settlement in settlements.iterrows():
        settlement_name = settlement.get("name")

        if pd.isna(settlement_name):
            settlement_name = "Unnamed settlement"

        settlement_name = str(settlement_name)

        settlement_osm_id = str(settlement["osm_id"])
        settlement_node = str(settlement["node"])

        baseline_row = baseline[
            baseline["osm_id"] == settlement_osm_id
        ]

        if baseline_row.empty:
            results.append(
                {
                    "osm_id": settlement_osm_id,
                    "name": settlement_name,
                    "status": "BASELINE_DATA_MISSING",
                    "baseline_distance_km": None,
                    "post_distance_km": None,
                    "route_increase_km": None,
                    "route_increase_percent": None,
                    "baseline_hospital": None,
                    "post_hospital": None,
                }
            )
            continue

        baseline_row = baseline_row.iloc[0]

        baseline_accessible = bool(
            baseline_row["baseline_accessible"]
        )

        baseline_distance_km = (
            float(baseline_row["baseline_distance_km"])
            if pd.notna(
                baseline_row["baseline_distance_km"]
            )
            else None
        )

        baseline_hospital_node = baseline_row[
            "nearest_hospital_node"
        ]

        if pd.isna(baseline_hospital_node):
            baseline_hospital_node = None
        else:
            baseline_hospital_node = str(
                baseline_hospital_node
            )

        if not baseline_accessible:
            results.append(
                {
                    "osm_id": settlement_osm_id,
                    "name": settlement_name,
                    "status": "BASELINE_UNREACHABLE",
                    "baseline_distance_km": baseline_distance_km,
                    "post_distance_km": None,
                    "route_increase_km": None,
                    "route_increase_percent": None,
                    "baseline_hospital": baseline_hospital_node,
                    "post_hospital": None,
                }
            )
            continue

        post_distance_m, post_hospital = get_nearest_hospital(
            disrupted_graph,
            settlement_node,
            hospital_nodes,
        )

        if post_distance_m is None:
            results.append(
                {
                    "osm_id": settlement_osm_id,
                    "name": settlement_name,
                    "status": "CUT_OFF",
                    "baseline_distance_km": baseline_distance_km,
                    "post_distance_km": None,
                    "route_increase_km": None,
                    "route_increase_percent": None,
                    "baseline_hospital": baseline_hospital_node,
                    "post_hospital": None,
                }
            )
            continue

        post_distance_km = post_distance_m / 1000.0

        route_increase_km = (
            post_distance_km - baseline_distance_km
        )

        if baseline_distance_km > 0:
            route_increase_percent = (
                route_increase_km
                / baseline_distance_km
                * 100.0
            )
        else:
            route_increase_percent = None

        if route_increase_km > 0.001:
            status = "LONGER_ROUTE"
        else:
            status = "NO_CHANGE"

        results.append(
            {
                "osm_id": settlement_osm_id,
                "name": settlement_name,
                "status": status,
                "baseline_distance_km": baseline_distance_km,
                "post_distance_km": post_distance_km,
                "route_increase_km": route_increase_km,
                "route_increase_percent": route_increase_percent,
                "baseline_hospital": baseline_hospital_node,
                "post_hospital": post_hospital,
            }
        )

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by=["status", "route_increase_km"],
        ascending=[True, False],
        na_position="last",
    )

    results_df.to_parquet(
        RESULT_PATH,
        index=False,
    )

    print()
    print("Network disruption results")
    print(
        results_df["status"]
        .value_counts()
        .to_string()
    )

    print()
    print("Potentially cut-off settlements:")

    cut_off = results_df[
        results_df["status"] == "CUT_OFF"
    ]

    if cut_off.empty:
        print("None")
    else:
        print(
            cut_off[
                [
                    "name",
                    "baseline_distance_km",
                    "baseline_hospital",
                ]
            ].to_string(index=False)
        )

    print()
    print("Settlements with longer routes:")

    longer_routes = results_df[
        results_df["status"] == "LONGER_ROUTE"
    ]

    if longer_routes.empty:
        print("None")
    else:
        print(
            longer_routes[
                [
                    "name",
                    "baseline_distance_km",
                    "post_distance_km",
                    "route_increase_km",
                    "route_increase_percent",
                ]
            ].to_string(index=False)
        )

    print()
    print("Baseline-unreachable settlements:")

    baseline_unreachable = results_df[
        results_df["status"] == "BASELINE_UNREACHABLE"
    ]

    if baseline_unreachable.empty:
        print("None")
    else:
        print(
            baseline_unreachable[
                ["name"]
            ].to_string(index=False)
        )

    print()
    print(f"Saved results: {RESULT_PATH}")
    print(
        f"Saved disrupted graph: "
        f"{DISRUPTED_GRAPH_PATH}"
    )


if __name__ == "__main__":
    main()