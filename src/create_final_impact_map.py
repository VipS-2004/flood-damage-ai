from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


BASE_DIR = Path(__file__).resolve().parents[1]

CORRIDOR_PATH = BASE_DIR / "outputs/drainage_corridor_100m.tif"
SAR_PATH = BASE_DIR / "outputs/joint_sar_evidence.tif"

BUILDINGS_PATH = (
    BASE_DIR
    / "data/processed/osm_20260727/buildings_utm.parquet"
)

ROADS_PATH = (
    BASE_DIR
    / "data/processed/osm_20260727/potentially_affected_roads.parquet"
)

BRIDGES_PATH = (
    BASE_DIR
    / "data/processed/osm_20260727/bridges_utm.parquet"
)

SETTLEMENTS_PATH = (
    BASE_DIR
    / "data/processed/osm_20260727/settlements_connected.parquet"
)

DISRUPTION_PATH = (
    BASE_DIR
    / "data/processed/osm_20260727/network_disruption_results.parquet"
)

OUTPUT_DIR = BASE_DIR / "outputs"

FINAL_MAP_PATH = OUTPUT_DIR / "final_impact_map.png"


def raster_to_polygons(raster_path):
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        transform = src.transform
        crs = src.crs

    mask = np.isfinite(data) & (data > 0)

    polygons = []

    for geom, value in shapes(
        data.astype(np.uint8),
        mask=mask,
        transform=transform,
    ):
        if value > 0:
            polygons.append(shape(geom))

    return gpd.GeoDataFrame(
        geometry=polygons,
        crs=crs,
    )


def get_label(row):
    name_en = row.get("name_en")

    if pd.notna(name_en):
        name_en = str(name_en).strip()

        if name_en and name_en.lower() != "nan":
            return name_en

    name = row.get("name")

    if pd.notna(name):
        name = str(name).strip()

        if name and name.lower() != "nan":
            return name

    return "Unnamed"


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Loading SAR evidence...")

    sar_gdf = raster_to_polygons(
        SAR_PATH
    )

    print(
        f"SAR evidence polygons: "
        f"{len(sar_gdf):,}"
    )

    print("Loading drainage corridor...")

    with rasterio.open(CORRIDOR_PATH) as src:
        corridor = src.read(1)
        transform = src.transform
        crs = src.crs

    corridor_mask = corridor > 0

    corridor_polygons = []

    for geom, value in shapes(
        corridor.astype(np.uint8),
        mask=corridor_mask,
        transform=transform,
    ):
        if value > 0:
            corridor_polygons.append(
                shape(geom)
            )

    corridor_gdf = gpd.GeoDataFrame(
        geometry=corridor_polygons,
        crs=crs,
    )

    print(
        f"Drainage corridor polygons: "
        f"{len(corridor_gdf):,}"
    )

    print("Loading infrastructure...")

    buildings = gpd.read_parquet(
        BUILDINGS_PATH
    )

    roads = gpd.read_parquet(
        ROADS_PATH
    )

    bridges = gpd.read_parquet(
        BRIDGES_PATH
    )

    print("Loading settlement results...")

    settlements = gpd.read_parquet(
        SETTLEMENTS_PATH
    )

    disruption = pd.read_parquet(
        DISRUPTION_PATH
    )

    settlements["osm_id"] = (
        settlements["osm_id"]
        .astype(str)
    )

    disruption["osm_id"] = (
        disruption["osm_id"]
        .astype(str)
    )

    settlements = settlements.merge(
        disruption[
            [
                "osm_id",
                "status",
                "baseline_distance_km",
                "post_distance_km",
                "route_increase_km",
                "route_increase_percent",
            ]
        ],
        on="osm_id",
        how="left",
    )

    cut_off = settlements[
        settlements["status"] == "CUT_OFF"
    ].copy()

    longer_routes = settlements[
        settlements["status"] == "LONGER_ROUTE"
    ].copy()

    print(
        f"Potentially cut-off settlements: "
        f"{len(cut_off)}"
    )

    print(
        f"Longer-route settlements: "
        f"{len(longer_routes)}"
    )

    print("Calculating infrastructure exposure...")

    corridor_union = (
        corridor_gdf.geometry.union_all()
    )

    buildings_exposed = buildings[
        buildings.geometry.intersects(
            corridor_union
        )
    ].copy()

    bridges_exposed = bridges[
        bridges.geometry.intersects(
            corridor_union
        )
    ].copy()

    print(
        f"Buildings in drainage corridor: "
        f"{len(buildings_exposed):,}"
    )

    print(
        f"Bridges in drainage corridor: "
        f"{len(bridges_exposed):,}"
    )

    print("Creating final presentation map...")

    fig, ax = plt.subplots(
        figsize=(15, 12)
    )

    corridor_gdf.plot(
        ax=ax,
        alpha=0.10,
        edgecolor="none",
        label="Drainage corridor",
    )

    if not sar_gdf.empty:
        sar_gdf.plot(
            ax=ax,
            alpha=0.75,
            edgecolor="none",
            label="Joint Sentinel-1 evidence",
        )

    roads.plot(
        ax=ax,
        linewidth=2.0,
        alpha=0.90,
        label="Potentially affected roads",
    )

    if not buildings_exposed.empty:
        buildings_exposed.plot(
            ax=ax,
            markersize=5,
            alpha=0.55,
            label="Buildings in corridor",
        )

    if not bridges_exposed.empty:
        bridges_exposed.plot(
            ax=ax,
            markersize=55,
            marker="s",
            alpha=0.95,
            label="Bridges in corridor",
        )

    if not longer_routes.empty:
        longer_routes.plot(
            ax=ax,
            markersize=65,
            marker="o",
            alpha=0.95,
            label="Longer hospital route",
        )

    if not cut_off.empty:
        cut_off.plot(
            ax=ax,
            markersize=90,
            marker="X",
            alpha=1.0,
            label="Potentially cut off",
        )

    print("Adding settlement labels...")

    for _, row in cut_off.iterrows():
        label = get_label(row)

        if label == "Unnamed":
            continue

        x = row.geometry.x
        y = row.geometry.y

        ax.annotate(
            label,
            xy=(x, y),
            xytext=(7, 7),
            textcoords="offset points",
            fontsize=8,
            fontweight="bold",
        )

    print("Adding major route-impact labels...")

    for _, row in longer_routes.iterrows():
        increase = row.get(
            "route_increase_km"
        )

        if pd.isna(increase):
            continue

        if float(increase) < 0.5:
            continue

        label = get_label(row)

        if label == "Unnamed":
            continue

        x = row.geometry.x
        y = row.geometry.y

        ax.annotate(
            label,
            xy=(x, y),
            xytext=(7, -12),
            textcoords="offset points",
            fontsize=7,
        )

    ax.set_title(
        "Flood Impact Evidence and Accessibility Scenario",
        fontsize=18,
        fontweight="bold",
        pad=18,
    )

    ax.text(
        0.01,
        0.01,
        "Joint Sentinel-1 change evidence is indicative, "
        "not a confirmed flood boundary. "
        "Road disruption is scenario-based.",
        transform=ax.transAxes,
        fontsize=9,
        alpha=0.75,
    )

    ax.set_xlabel(
        "UTM Easting (m)",
        fontsize=10,
    )

    ax.set_ylabel(
        "UTM Northing (m)",
        fontsize=10,
    )

    ax.grid(
        alpha=0.18,
    )

    ax.legend(
        loc="upper right",
        fontsize=9,
        framealpha=0.95,
    )

    plt.tight_layout()

    plt.savefig(
        FINAL_MAP_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print()
    print(
        f"Final map saved to:"
    )
    print(FINAL_MAP_PATH)


if __name__ == "__main__":
    main()