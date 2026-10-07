import geopandas as gpd
from pathlib import Path

INPUT_DIR = Path("data/raw/osm_20260727")
OUTPUT_DIR = Path("data/processed/osm_20260727")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

roads = gpd.read_parquet(INPUT_DIR / "roads.parquet")
bridges = gpd.read_parquet(INPUT_DIR / "bridges.parquet")
buildings = gpd.read_parquet(INPUT_DIR / "buildings.parquet")

roads["highway"] = roads["tags"].apply(
    lambda x: dict(x).get("highway")
)

road_priority = {
    "trunk": 5,
    "primary": 5,
    "tertiary": 4,
    "secondary": 4,
    "residential": 3,
    "unclassified": 2,
    "service": 2,
    "track": 1,
    "path": 1,
    "footway": 1,
    "steps": 1,
    "construction": 1,
}

roads["priority"] = roads["highway"].map(road_priority).fillna(1)

important_roads = roads[roads["priority"] >= 2].copy()

roads.to_parquet(OUTPUT_DIR / "roads_all.parquet")
important_roads.to_parquet(OUTPUT_DIR / "roads_important.parquet")
bridges.to_parquet(OUTPUT_DIR / "bridges.parquet")
buildings.to_parquet(OUTPUT_DIR / "buildings.parquet")

print(f"Buildings: {len(buildings)}")
print(f"All roads: {len(roads)}")
print(f"Important roads: {len(important_roads)}")
print(f"Bridges: {len(bridges)}")

print("\nImportant road classes:")
print(
    important_roads["highway"]
    .value_counts()
    .to_string()
)