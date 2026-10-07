import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from pathlib import Path

OSM_DIR = Path("data/processed/osm_20260727")
CORRIDOR = Path("outputs/drainage_corridor_100m.tif")
OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with rasterio.open(CORRIDOR) as src:
    corridor = src.read(1)
    transform = src.transform
    crs = src.crs

mask = corridor == 1

geometries = [
    shape(geom)
    for geom, value in shapes(corridor, mask=mask, transform=transform)
    if value == 1
]

corridor_gdf = gpd.GeoDataFrame(
    {"corridor": [1] * len(geometries)},
    geometry=geometries,
    crs=crs
)

corridor_geom = corridor_gdf.geometry.union_all()

for name in ["buildings", "roads", "bridges"]:
    file = OSM_DIR / f"{name}_utm.parquet"
    gdf = gpd.read_parquet(file)

    exposed = gdf[gdf.geometry.intersects(corridor_geom)].copy()

    output_file = OUTPUT_DIR / f"{name}_drainage_corridor_exposed.parquet"
    exposed.to_parquet(output_file)

    print(f"{name}:")
    print(f"  Total: {len(gdf)}")
    print(f"  Corridor exposed: {len(exposed)}")
    print(f"  Saved: {output_file}")
    print()