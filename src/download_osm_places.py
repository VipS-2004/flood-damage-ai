import os
from pathlib import Path

import geopandas as gpd
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OHSOME_API_KEY")

if not API_KEY:
    raise RuntimeError("OHSOME_API_KEY not found in .env")

AOI = {
    "west": 85.28,
    "south": 28.10,
    "east": 85.60,
    "north": 28.34,
}

SNAPSHOT_DATE = "2026-07-27"

OUTPUT_DIR = Path("data/raw/osm_20260727")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://api.heigit.org/ohsome-api/v2-rc/extraction/features.parquet"


def download_osm(name, filter_query, output_file):
    print(f"Downloading {name}...")

    payload = {
    "aoi": (
        f"POLYGON(("
        f"{AOI['west']} {AOI['south']},"
        f"{AOI['east']} {AOI['south']},"
        f"{AOI['east']} {AOI['north']},"
        f"{AOI['west']} {AOI['north']},"
        f"{AOI['west']} {AOI['south']}"
        f"))"
    ),
    "filter": filter_query,
    "time": SNAPSHOT_DATE,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    response = requests.post(
        URL,
        json=payload,
        headers=headers,
        timeout=300,
    )

    print(f"HTTP status: {response.status_code}")

    if response.status_code != 200:
        print(response.text[:1000])
        response.raise_for_status()

    output_path = OUTPUT_DIR / output_file
    output_path.write_bytes(response.content)

    print(f"Saved: {output_path}")
    print(f"Size: {output_path.stat().st_size:,} bytes")

    gdf = gpd.read_parquet(output_path)

    print(f"Features: {len(gdf)}")
    print(f"CRS: {gdf.crs}")

    if len(gdf) > 0:
        print(gdf[["osm_id", "tags"]].head())

    print()


download_osm(
    "settlements",
    "place=* and geometry:point",
    "settlements.parquet",
)

download_osm(
    "hospitals",
    "amenity=hospital and geometry:point",
    "hospitals.parquet",
)

print("Done.")