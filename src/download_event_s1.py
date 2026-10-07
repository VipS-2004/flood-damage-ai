import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

PROCESS_URL = "https://sh.dataspace.copernicus.eu/process/v1"

BBOX = [
    85.28,
    28.10,
    85.60,
    28.34
]

OUTPUT_DIR = "data/raw"


def get_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "COPERNICUS_CLIENT_ID or COPERNICUS_CLIENT_SECRET "
            "is missing from .env"
        )

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()["access_token"]


def download_scene(token, date, band):
    start = f"{date}T00:00:00Z"
    end = f"{date}T23:59:59Z"

    evalscript = f"""
//VERSION=3

function setup() {{
    return {{
        input: ["{band}"],
        output: {{
            bands: 1,
            sampleType: "FLOAT32"
        }}
    }};
}}

function evaluatePixel(sample) {{
    return [sample.{band}];
}}
"""

    payload = {
        "input": {
            "bounds": {
                "bbox": BBOX
            },
            "data": [
                {
                    "type": "sentinel-1-grd",

                    "dataFilter": {
                        "timeRange": {
                            "from": start,
                            "to": end
                        },
                        "orbitDirection": "ASCENDING",
                        "acquisitionMode": "IW",
                        "polarization": "DV"
                    },

                    "processing": {
                        "orthorectify": True,
                        "demInstance": "COPERNICUS_30",
                        "backCoeff": "GAMMA0_TERRAIN"
                    }
                }
            ]
        },

        "output": {
            "width": 1200,
            "height": 1000,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }
            ]
        },

        "evalscript": evalscript
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "image/tiff"
    }

    print(f"Downloading {date} {band} with GAMMA0_TERRAIN...")

    response = requests.post(
        PROCESS_URL,
        headers=headers,
        json=payload,
        timeout=180
    )

    print("HTTP status:", response.status_code)

    if not response.ok:
        print("Response:")
        print(response.text)

    response.raise_for_status()

    filename = (
        f"sentinel1_{date.replace('-', '')}"
        f"_{band}_gamma0terrain.tif"
    )

    filepath = os.path.join(
        OUTPUT_DIR,
        filename
    )

    with open(filepath, "wb") as f:
        f.write(response.content)

    print(f"Saved: {filepath}")
    print(f"Size: {len(response.content) / 1024:.1f} KB")
    print()


def main():
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print("Authenticating with Copernicus...")

    token = get_token()

    print("Authentication successful.")
    print()

    download_scene(
        token,
        "2026-08-16",
        "VV"
    )

    download_scene(
        token,
        "2026-08-16",
        "VH"
    )

    download_scene(
        token,
        "2026-08-28",
        "VV"
    )

    download_scene(
        token,
        "2026-08-28",
        "VH"
    )

    print("All terrain-corrected event scenes downloaded.")


if __name__ == "__main__":
    main()