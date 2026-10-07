import geopandas as gpd
from pathlib import Path

INPUT_DIR = Path("data/raw/osm_20260727")
OUTPUT_DIR = Path("data/processed/osm_20260727")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_CRS = "EPSG:32645"

layers = [
    "buildings",
    "roads",
    "bridges",
]

for name in layers:
    input_file = INPUT_DIR / f"{name}.parquet"
    output_file = OUTPUT_DIR / f"{name}_utm.parquet"

    gdf = gpd.read_parquet(input_file)

    print(f"{name}: {len(gdf)} features")
    print(f"Original CRS: {gdf.crs}")

    gdf_utm = gdf.to_crs(TARGET_CRS)

    gdf_utm.to_parquet(output_file)

    print(f"Saved: {output_file}")
    print(f"Projected CRS: {gdf_utm.crs}")
    print()