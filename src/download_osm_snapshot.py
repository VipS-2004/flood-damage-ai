import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OHSOME_API_KEY")

if not API_KEY:
    raise RuntimeError("OHSOME_API_KEY not found in .env")

API_URL = "https://api.heigit.org/ohsome-api/v2-rc/extraction/features.parquet"

AOI = [85.28, 28.10, 85.60, 28.34]
TIME = "2026-07-27"

OUTPUT_DIR = Path("data/raw/osm_20260727")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

layers = {
    "buildings": "building=* and building!=no and geometry:polygon",
    "roads": "highway=* and geometry:line",
    "bridges": "bridge=* and geometry:line",
}

headers = {
    "Authorization": API_KEY
}

for name, osm_filter in layers.items():
    print(f"Downloading {name}...")

    payload = {
        "aoi": AOI,
        "filter": osm_filter,
        "time": TIME
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=300
    )

    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text[:1000])
        raise RuntimeError(f"Failed to download {name}")

    output_file = OUTPUT_DIR / f"{name}.parquet"
    output_file.write_bytes(response.content)

    print(f"Saved: {output_file}")
    print(f"Size: {len(response.content):,} bytes")