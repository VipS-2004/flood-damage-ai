import geopandas as gpd
from pathlib import Path

osm_dir = Path("data/raw/osm_20260727")

for file in osm_dir.glob("*.parquet"):
    gdf = gpd.read_parquet(file)

    print(f"\n{file.name}")
    print("=" * len(file.name))

    print(gdf["tags"].head(5).to_string(index=False))