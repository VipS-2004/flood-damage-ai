import os
import requests
from dotenv import load_dotenv
import rasterio
import numpy as np


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


def get_token():

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


def download_scl(token, date):

    evalscript = """
//VERSION=3

function setup() {
    return {
        input: ["SCL"],
        output: {
            bands: 1,
            sampleType: "UINT8"
        }
    };
}

function evaluatePixel(sample) {
    return [sample.SCL];
}
"""

    payload = {
        "input": {
            "bounds": {
                "bbox": BBOX
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{date}T00:00:00Z",
                            "to": f"{date}T23:59:59Z"
                        },
                        "maxCloudCoverage": 100
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
        "Content-Type": "application/json"
    }

    print(f"Downloading SCL for {date}...")

    response = requests.post(
        PROCESS_URL,
        headers=headers,
        json=payload,
        timeout=180
    )

    print("HTTP status:", response.status_code)

    response.raise_for_status()

    filename = f"data/raw/sentinel2_{date}_SCL.tif"

    with open(filename, "wb") as f:
        f.write(response.content)

    print("Saved:", filename)


def analyze_scl(filepath):

    with rasterio.open(filepath) as src:

        scl = src.read(1)

    total = scl.size

    clear_classes = [
        4,
        5,
        6,
        11
    ]

    cloud_classes = [
        7,
        8,
        9,
        10
    ]

    clear = np.isin(
        scl,
        clear_classes
    )

    clouds = np.isin(
        scl,
        cloud_classes
    )

    print()
    print("Total pixels:", total)

    print(
        "Clear/useful pixels:",
        clear.sum(),
        f"({clear.sum() / total * 100:.2f}%)"
    )

    print(
        "Cloud pixels:",
        clouds.sum(),
        f"({clouds.sum() / total * 100:.2f}%)"
    )

    print()
    print("SCL class counts:")

    classes, counts = np.unique(
        scl,
        return_counts=True
    )

    for cls, count in zip(
        classes,
        counts
    ):

        print(
            f"Class {cls}: {count}"
        )


print("Authenticating...")

token = get_token()

print("Authentication successful.")
print()

date = "2026-08-27"

download_scl(
    token,
    date
)

analyze_scl(
    f"data/raw/sentinel2_{date}_SCL.tif"
)