from pathlib import Path

import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString


ROADS_PATH = "data/processed/osm_20260727/roads_all.parquet"

OUTPUT_DIR = Path("data/processed/osm_20260727")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_GRAPH = OUTPUT_DIR / "road_network_metric.graphml"

TARGET_CRS = "EPSG:32645"


print("Loading roads...")

roads = gpd.read_parquet(ROADS_PATH)

print(f"Road features: {len(roads)}")
print(f"Original CRS: {roads.crs}")

roads = roads[roads["geom"].notna()].copy()

roads = roads.set_geometry("geom")

roads = roads.to_crs(TARGET_CRS)

print(f"Projected CRS: {roads.crs}")

graph = nx.Graph()

for _, row in roads.iterrows():
    geom = row["geom"]

    if geom is None or geom.is_empty:
        continue

    if geom.geom_type == "LineString":
        lines = [geom]

    elif geom.geom_type == "MultiLineString":
        lines = list(geom.geoms)

    else:
        continue

    for line in lines:
        coordinates = list(line.coords)

        if len(coordinates) < 2:
            continue

        for start, end in zip(coordinates[:-1], coordinates[1:]):
            start_node = f"{start[0]:.3f},{start[1]:.3f}"
            end_node = f"{end[0]:.3f},{end[1]:.3f}"

            segment = LineString([start, end])
            length_m = segment.length

            graph.add_node(
                start_node,
                x=float(start[0]),
                y=float(start[1]),
            )

            graph.add_node(
                end_node,
                x=float(end[0]),
                y=float(end[1]),
            )

            graph.add_edge(
                start_node,
                end_node,
                length_m=float(length_m),
                osm_id=str(row["osm_id"]),
                highway=str(row["highway"]),
                priority=int(row["priority"]),
            )


print(f"Graph nodes: {graph.number_of_nodes()}")
print(f"Graph edges: {graph.number_of_edges()}")

lengths = [
    data["length_m"]
    for _, _, data in graph.edges(data=True)
]

print(f"Minimum edge length: {min(lengths):.2f} m")
print(f"Median edge length: {sorted(lengths)[len(lengths) // 2]:.2f} m")
print(f"Maximum edge length: {max(lengths):.2f} m")

nx.write_graphml(graph, OUTPUT_GRAPH)

print(f"Saved: {OUTPUT_GRAPH}")