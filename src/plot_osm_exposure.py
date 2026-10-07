import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
from pathlib import Path

CORRIDOR = Path("outputs/valley_corridor.tif")
OSM_DIR = Path("data/processed/osm_20260727")
OUTPUT = Path("outputs/osm_corridor_exposure.png")

with rasterio.open(CORRIDOR) as src:
    corridor = src.read(1)
    extent = (
        src.bounds.left,
        src.bounds.right,
        src.bounds.bottom,
        src.bounds.top,
    )

buildings = gpd.read_parquet(OSM_DIR / "buildings_utm.parquet")
roads = gpd.read_parquet(OSM_DIR / "roads_utm.parquet")
bridges = gpd.read_parquet(OSM_DIR / "bridges_utm.parquet")

buildings_exposed = gpd.read_parquet(
    "outputs/buildings_corridor_exposed.parquet"
)
roads_exposed = gpd.read_parquet(
    "outputs/roads_corridor_exposed.parquet"
)
bridges_exposed = gpd.read_parquet(
    "outputs/bridges_corridor_exposed.parquet"
)

fig, ax = plt.subplots(figsize=(12, 10))

show(
    corridor,
    ax=ax,
    extent=extent,
    alpha=0.35
)

buildings.plot(
    ax=ax,
    markersize=1,
    alpha=0.15
)

roads.plot(
    ax=ax,
    linewidth=0.4,
    alpha=0.3
)

bridges.plot(
    ax=ax,
    linewidth=1.5,
    alpha=0.5
)

buildings_exposed.plot(
    ax=ax,
    markersize=3,
    alpha=0.7
)

roads_exposed.plot(
    ax=ax,
    linewidth=1.2,
    alpha=0.8
)

bridges_exposed.plot(
    ax=ax,
    linewidth=3,
    alpha=1.0
)

ax.set_title(
    "Pre-event OSM Infrastructure Exposure to Terrain-Derived Valley Corridor"
)

ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")

plt.tight_layout()
plt.savefig(OUTPUT, dpi=200, bbox_inches="tight")
plt.close()

print(f"Saved: {OUTPUT}")
print(f"Buildings exposed: {len(buildings_exposed)}")
print(f"Roads exposed: {len(roads_exposed)}")
print(f"Bridges exposed: {len(bridges_exposed)}")