from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


BRIDGES_PATH = "data/processed/osm_20260727/bridges_utm.parquet"
SAR_PATH = "outputs/joint_sar_evidence.tif"
CORRIDOR_PATH = "outputs/drainage_corridor_100m.tif"

OUTPUT_DIR = Path("data/processed/osm_20260727")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "potentially_affected_bridges.parquet"

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

print(f"Joint SAR + corridor pixels: {evidence_mask.sum():,}")


print("Converting evidence to polygons...")

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


if not evidence_polygons:
    raise RuntimeError("No evidence polygons found.")


evidence_gdf = gpd.GeoDataFrame(
    {"geometry": evidence_polygons},
    geometry="geometry",
    crs=sar_crs,
)

evidence_gdf = evidence_gdf.to_crs(TARGET_CRS)

evidence_union = evidence_gdf.geometry.union_all()


print("Loading OSM bridges...")

bridges = gpd.read_parquet(BRIDGES_PATH)

bridges = bridges.set_geometry("geom")

bridges = bridges.to_crs(TARGET_CRS)

bridges = bridges[bridges["geom"].notna()].copy()

print(f"Bridges loaded: {len(bridges)}")


print("Finding potentially affected bridges...")

affected_rows = []

for _, bridge in bridges.iterrows():

    bridge_geom = bridge["geom"]

    if bridge_geom is None or bridge_geom.is_empty:
        continue

    if not bridge_geom.intersects(evidence_union):
        continue

    intersection = bridge_geom.intersection(evidence_union)

    if intersection.is_empty:
        continue

    affected_rows.append({
        "osm_id": str(bridge["osm_id"]),
        "highway": bridge.get("highway"),
        "ref": bridge.get("ref"),
        "road_length_m": float(bridge_geom.length),
        "affected_length_m": float(intersection.length),
        "geom": bridge_geom,
    })


if affected_rows:
    affected_bridges = gpd.GeoDataFrame(
        affected_rows,
        geometry="geom",
        crs=TARGET_CRS,
    )
else:
    affected_bridges = gpd.GeoDataFrame(
        columns=[
            "osm_id",
            "highway",
            "ref",
            "road_length_m",
            "affected_length_m",
            "geom",
        ],
        geometry="geom",
        crs=TARGET_CRS,
    )


print("\nPotentially affected bridge summary:")

print(f"Bridges intersecting evidence: {len(affected_bridges)}")


if len(affected_bridges) > 0:

    print(
        f"Total bridge geometry length: "
        f"{affected_bridges['road_length_m'].sum():.2f} m"
    )

    print(
        f"Bridge geometry overlapping evidence: "
        f"{affected_bridges['affected_length_m'].sum():.2f} m"
    )

    print("\nPotentially affected bridges:")

    print(
        affected_bridges[
            [
                "osm_id",
                "highway",
                "ref",
                "road_length_m",
                "affected_length_m",
            ]
        ].to_string(index=False)
    )

else:
    print("No bridges intersect the evidence.")


affected_bridges.to_parquet(
    OUTPUT_PATH,
    index=False,
)

print(f"\nSaved: {OUTPUT_PATH}")
print("Done.")