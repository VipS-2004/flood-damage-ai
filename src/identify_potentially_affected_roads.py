from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


ROADS_PATH = "data/processed/osm_20260727/roads_all.parquet"
SAR_PATH = "outputs/joint_sar_evidence.tif"
CORRIDOR_PATH = "outputs/drainage_corridor_100m.tif"

OUTPUT_DIR = Path("data/processed/osm_20260727")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "potentially_affected_roads.parquet"

TARGET_CRS = "EPSG:32645"


print("Loading joint SAR evidence...")

with rasterio.open(SAR_PATH) as src:
    sar = src.read(1)
    sar_transform = src.transform
    sar_crs = src.crs

print(f"SAR CRS: {sar_crs}")
print(f"SAR shape: {sar.shape}")

print("Loading drainage corridor...")

with rasterio.open(CORRIDOR_PATH) as src:
    corridor = src.read(1).astype(bool)
    corridor_transform = src.transform
    corridor_crs = src.crs

print(f"Corridor CRS: {corridor_crs}")
print(f"Corridor pixels: {corridor.sum():,}")


print("Combining SAR evidence with drainage corridor...")

if sar.shape != corridor.shape:
    raise RuntimeError(
        f"Raster shape mismatch: SAR={sar.shape}, corridor={corridor.shape}"
    )

if sar_crs != corridor_crs:
    raise RuntimeError(
        f"Raster CRS mismatch: SAR={sar_crs}, corridor={corridor_crs}"
    )

if sar_transform != corridor_transform:
    raise RuntimeError("SAR and drainage corridor grids do not match.")


evidence_mask = (
    np.isfinite(sar)
    & (sar > 0)
    & corridor
)

print(f"Joint SAR pixels: {(sar > 0).sum():,}")
print(f"Joint SAR + corridor pixels: {evidence_mask.sum():,}")


print("Converting evidence pixels to polygons...")

evidence_polygons = []

for geom, value in shapes(
    evidence_mask.astype(np.uint8),
    mask=evidence_mask,
    transform=sar_transform,
):
    if value == 1:
        polygon = shape(geom)

        if not polygon.is_empty:
            evidence_polygons.append(polygon)


print(f"Evidence polygons: {len(evidence_polygons)}")

if not evidence_polygons:
    raise RuntimeError("No SAR evidence polygons found.")


evidence_gdf = gpd.GeoDataFrame(
    {"geometry": evidence_polygons},
    geometry="geometry",
    crs=sar_crs,
)

evidence_gdf = evidence_gdf.to_crs(TARGET_CRS)

evidence_gdf["evidence_area_m2"] = evidence_gdf.geometry.area

print(
    f"Total evidence area: "
    f"{evidence_gdf['evidence_area_m2'].sum():.2f} m²"
)


print("Loading OSM roads...")

roads = gpd.read_parquet(ROADS_PATH)

roads = roads.set_geometry("geom")

roads = roads.to_crs(TARGET_CRS)

roads = roads[roads["geom"].notna()].copy()

print(f"Roads loaded: {len(roads)}")


print("Creating unified evidence geometry...")

evidence_union = evidence_gdf.geometry.union_all()

print("Finding potentially affected roads...")

affected_rows = []

for _, road in roads.iterrows():

    road_geom = road["geom"]

    if road_geom is None or road_geom.is_empty:
        continue

    if not road_geom.intersects(evidence_union):
        continue

    intersection = road_geom.intersection(evidence_union)

    if intersection.is_empty:
        continue

    affected_length = intersection.length
    road_length = road_geom.length

    affected_rows.append({
        "osm_id": str(road["osm_id"]),
        "highway": road["highway"],
        "priority": int(road["priority"]),
        "road_length_m": float(road_length),
        "affected_length_m": float(affected_length),
        "affected_fraction": float(
            affected_length / road_length
        ) if road_length > 0 else 0.0,
        "geom": road_geom,
    })


affected_roads = gpd.GeoDataFrame(
    affected_rows,
    geometry="geom",
    crs=TARGET_CRS,
)


print("\nPotentially affected road summary:")

print(f"Roads intersecting evidence: {len(affected_roads)}")

if len(affected_roads) > 0:

    print(
        f"Total road length: "
        f"{affected_roads['road_length_m'].sum() / 1000:.2f} km"
    )

    print(
        f"Road length overlapping evidence: "
        f"{affected_roads['affected_length_m'].sum() / 1000:.2f} km"
    )

    print("\nBy highway type:")

    print(
        affected_roads["highway"]
        .value_counts()
        .to_string()
    )

    print("\nMost affected segments:")

    print(
        affected_roads[
            [
                "osm_id",
                "highway",
                "priority",
                "road_length_m",
                "affected_length_m",
                "affected_fraction",
            ]
        ]
        .sort_values(
            "affected_fraction",
            ascending=False,
        )
        .head(20)
        .to_string(index=False)
    )

else:
    print("No road segments intersect the evidence.")


affected_roads.to_parquet(
    OUTPUT_PATH,
    index=False,
)

print(f"\nSaved: {OUTPUT_PATH}")
print("Done.")