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

# Same technical test AOI as Sentinel-1
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
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]


def download_dem(token):

    evalscript = """
    //VERSION=3

    function setup() {
        return {
            input: ["DEM"],
            output: {
                bands: 1,
                sampleType: SampleType.FLOAT32
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.DEM];
    }
    """

    request_body = {
        "input": {
            "bounds": {
                "bbox": BBOX
            },
            "data": [
                {
                    "type": "dem",
                    "dataFilter": {
                        "demInstance": "COPERNICUS_90"
                    },
                    "processing": {
                        "upsampling": "BILINEAR",
                        "downsampling": "BILINEAR"
                    }
                }
            ]
        },
        "output": {
            "width": 1000,
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

    response = requests.post(
        PROCESS_URL,
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=request_body,
        timeout=120
    )

    print("DEM API status:", response.status_code)

    response.raise_for_status()

    output_path = "data/raw/copernicus_dem.tif"

    with open(output_path, "wb") as f:
        f.write(response.content)

    print("Saved:", output_path)
    print("Size:", len(response.content), "bytes")


def main():

    token = get_token()

    print("OAuth: OK")

    download_dem(token)


if __name__ == "__main__":
    main()