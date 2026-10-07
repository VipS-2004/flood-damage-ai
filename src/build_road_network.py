from pathlib import Path

import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString


ROADS_PATH = "data/processed/osm_20260727/roads_all.parquet"
OUTPUT_DIR = Path("data/processed/osm_20260727")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_GRAPH = OUTPUT_DIR / "road_network.graphml"


roads = gpd.read_parquet(ROADS_PATH)

print(f"Loaded roads: {len(roads)}")
print(f"CRS: {roads.crs}")

roads = roads[roads["geom"].notna()].copy()

graph = nx.Graph()

for _, row in roads.iterrows():
    geom = row["geom"]

    if geom is None:
        continue

    geometries = [geom]

    if geom.geom_type == "MultiLineString":
        geometries = list(geom.geoms)

    for line in geometries:
        coordinates = list(line.coords)

        if len(coordinates) < 2:
            continue

        for start, end in zip(coordinates[:-1], coordinates[1:]):
            start_node = f"{start[0]:.7f},{start[1]:.7f}"
            end_node = f"{end[0]:.7f},{end[1]:.7f}"

            segment_length = LineString([start, end]).length

            graph.add_node(
                start_node,
                longitude=start[0],
                latitude=start[1],
            )

            graph.add_node(
                end_node,
                longitude=end[0],
                latitude=end[1],
            )

            graph.add_edge(
                start_node,
                end_node,
                length=segment_length,
                osm_id=str(row["osm_id"]),
                highway=str(row["highway"]),
                priority=int(row["priority"]),
            )


print(f"Graph nodes: {graph.number_of_nodes()}")
print(f"Graph edges: {graph.number_of_edges()}")

nx.write_graphml(graph, OUTPUT_GRAPH)

print(f"Saved: {OUTPUT_GRAPH}")