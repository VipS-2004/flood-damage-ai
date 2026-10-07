from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import Point


SETTLEMENTS_PATH = "data/raw/osm_20260727/settlements.parquet"
HOSPITALS_PATH = "data/raw/osm_20260727/hospitals.parquet"
GRAPH_PATH = "data/processed/osm_20260727/road_network_metric.graphml"

OUTPUT_DIR = Path("data/processed/osm_20260727")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SETTLEMENT_OUTPUT = OUTPUT_DIR / "settlements_connected.parquet"
HOSPITAL_OUTPUT = OUTPUT_DIR / "hospitals_connected.parquet"

TARGET_CRS = "EPSG:32645"


def tags_to_dict(tags):
    if isinstance(tags, list):
        return dict(tags)
    return {}


def get_metric_road_nodes(graph):
    rows = []

    for node, data in graph.nodes(data=True):
        rows.append({
            "node": str(node),
            "x": float(data["x"]),
            "y": float(data["y"]),
        })

    return gpd.GeoDataFrame(
        rows,
        geometry=[
            Point(row["x"], row["y"])
            for _, row in pd.DataFrame(rows).iterrows()
        ],
        crs=TARGET_CRS,
    )


print("Loading metric road graph...")

graph = nx.read_graphml(GRAPH_PATH)

print(f"Road graph nodes: {graph.number_of_nodes()}")
print(f"Road graph edges: {graph.number_of_edges()}")

road_nodes = get_metric_road_nodes(graph)

print(f"Road nodes available for matching: {len(road_nodes)}")


print("Loading settlements...")

settlements_raw = gpd.read_parquet(SETTLEMENTS_PATH)

settlement_rows = []

for _, row in settlements_raw.iterrows():

    tags = tags_to_dict(row["tags"])

    place_type = tags.get("place")

    if place_type not in {"hamlet", "village", "suburb"}:
        continue

    name = tags.get("name")
    name_en = tags.get("name:en")

    settlement_rows.append({
        "osm_id": str(row["osm_id"]),
        "name": name,
        "name_en": name_en,
        "place": place_type,
        "geometry": row["geom"],
    })


settlements = gpd.GeoDataFrame(
    settlement_rows,
    geometry="geometry",
    crs="EPSG:4326",
)

settlements = settlements.to_crs(TARGET_CRS)

print(f"Settlements selected: {len(settlements)}")

print("Connecting settlements to metric road nodes...")

settlements_connected = gpd.sjoin_nearest(
    settlements,
    road_nodes[["node", "geometry"]],
    how="left",
    distance_col="distance_to_road_m",
)

settlements_connected = settlements_connected.drop(
    columns=["index_right"],
    errors="ignore",
)

settlements_connected.to_parquet(
    SETTLEMENT_OUTPUT,
    index=False,
)

print(f"Saved: {SETTLEMENT_OUTPUT}")


print("Loading hospitals...")

hospitals_raw = gpd.read_parquet(HOSPITALS_PATH)

hospital_rows = []

for _, row in hospitals_raw.iterrows():

    tags = tags_to_dict(row["tags"])

    hospital_rows.append({
        "osm_id": str(row["osm_id"]),
        "name": tags.get("name"),
        "amenity": tags.get("amenity"),
        "geometry": row["geom"],
    })


hospitals = gpd.GeoDataFrame(
    hospital_rows,
    geometry="geometry",
    crs="EPSG:4326",
)

hospitals = hospitals.to_crs(TARGET_CRS)

print(f"Hospitals: {len(hospitals)}")

print("Connecting hospitals to metric road nodes...")

hospitals_connected = gpd.sjoin_nearest(
    hospitals,
    road_nodes[["node", "geometry"]],
    how="left",
    distance_col="distance_to_road_m",
)

hospitals_connected = hospitals_connected.drop(
    columns=["index_right"],
    errors="ignore",
)

hospitals_connected.to_parquet(
    HOSPITAL_OUTPUT,
    index=False,
)

print(f"Saved: {HOSPITAL_OUTPUT}")


print("\nSettlement connections:")

print(
    settlements_connected[
        ["name_en", "name", "place", "node", "distance_to_road_m"]
    ].to_string(index=False)
)


print("\nHospital connections:")

print(
    hospitals_connected[
        ["name", "node", "distance_to_road_m"]
    ].to_string(index=False)
)


print("\nDone.")