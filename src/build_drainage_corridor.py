import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from pathlib import Path
import numpy as np

INPUT = Path("outputs/main_drainage_10000.tif")
OUTPUT = Path("outputs/drainage_corridor_100m.tif")

BUFFER_METERS = 100

with rasterio.open(INPUT) as src:
    drainage = src.read(1)
    transform = src.transform
    crs = src.crs
    profile = src.profile.copy()

mask = drainage == 1

geometries = [
    shape(geom)
    for geom, value in shapes(
        drainage,
        mask=mask,
        transform=transform
    )
    if value == 1
]

drainage_gdf = gpd.GeoDataFrame(
    {"value": [1] * len(geometries)},
    geometry=geometries,
    crs=crs
)

drainage_geom = drainage_gdf.geometry.union_all()

corridor_geom = drainage_geom.buffer(BUFFER_METERS)

height, width = drainage.shape

rows, cols = np.indices((height, width))

xs, ys = rasterio.transform.xy(
    transform,
    rows,
    cols
)

points = gpd.GeoSeries(
    gpd.points_from_xy(
        np.asarray(xs).ravel(),
        np.asarray(ys).ravel()
    ),
    crs=crs
)

inside = points.within(corridor_geom).to_numpy()

corridor = inside.reshape((height, width)).astype(np.uint8)

profile.update(
    dtype="uint8",
    count=1,
    nodata=0
)

with rasterio.open(OUTPUT, "w", **profile) as dst:
    dst.write(corridor, 1)

print(f"Drainage components: {len(geometries)}")
print(f"Buffer: {BUFFER_METERS} m")
print(f"Corridor pixels: {np.sum(corridor == 1):,}")
print(f"Saved: {OUTPUT}")