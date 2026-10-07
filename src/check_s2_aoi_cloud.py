import requests
import rasterio
from rasterio.io import MemoryFile
from dotenv import load_dotenv
import os
import numpy as np
import matplotlib.pyplot as plt

load_dotenv()

CLIENT_ID = os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("COPERNICUS_CLIENT_SECRET")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

PROCESS_URL = "https://sh.dataspace.copernicus.eu/process/v1"

AOI = [85.28, 28.10, 85.60, 28.34]

SCENES = {
    "20260827": (
        "2026-08-27T00:00:00Z",
        "2026-08-28T00:00:00Z",
    ),
}

token_response = requests.post(
    TOKEN_URL,
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
)

token_response.raise_for_status()

access_token = token_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

for date, (start_time, end_time) in SCENES.items():

    payload = {
        "input": {
            "bounds": {
                "bbox": AOI
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": start_time,
                            "to": end_time
                        },
                        "mosaickingOrder": "mostRecent"
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
        "evalscript": """
        //VERSION=3

        function setup() {
            return {
                input: ["SCL", "dataMask"],
                output: {
                    bands: 2,
                    sampleType: "UINT8"
                }
            };
        }

        function evaluatePixel(sample) {
            return [
                sample.SCL,
                sample.dataMask
            ];
        }
        """
    }

    response = requests.post(
        PROCESS_URL,
        headers=headers,
        json=payload,
    )

    print()
    print(date)
    print("HTTP status:", response.status_code)

    response.raise_for_status()

    with MemoryFile(response.content) as memfile:
        with memfile.open() as src:
            scl = src.read(1)
            data_mask = src.read(2)

    print("SCL unique values:", np.unique(scl))
    print("Data mask unique values:", np.unique(data_mask))

    valid = data_mask == 1

    cloud = np.isin(scl, [8, 9, 10])
    shadow = scl == 3

    valid_count = valid.sum()
    cloud_count = (cloud & valid).sum()
    shadow_count = (shadow & valid).sum()

    print("Valid pixels:", valid_count)

    if valid_count > 0:
        print(
            "Cloud percentage:",
            round(100 * cloud_count / valid_count, 2)
        )
        print(
            "Cloud shadow percentage:",
            round(100 * shadow_count / valid_count, 2)
        )
    else:
        print("Cloud percentage: N/A")
        print("Cloud shadow percentage: N/A")

    plt.figure(figsize=(10, 8))
    plt.imshow(scl)
    plt.colorbar(label="SCL class")
    plt.title(f"Sentinel-2 SCL {date}")
    plt.tight_layout()

    output_path = f"outputs/s2_scl_{date}.png"

    plt.savefig(
        output_path,
        dpi=150
    )

    plt.close()

    print("Saved:", output_path)