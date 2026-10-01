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

BBOX = [85.50, 27.80, 86.20, 28.30]

DATES = {
    "20260819": "2026-08-19",
    "20260831": "2026-08-31",
}


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


def download_sentinel1(token, date, polarization, output_path):

    evalscript = f"""
    //VERSION=3

    function setup() {{
        return {{
            input: ["{polarization}"],
            output: {{
                bands: 1,
                sampleType: SampleType.FLOAT32
            }}
        }};
    }}

    function evaluatePixel(sample) {{
        return [sample.{polarization}];
    }}
    """

    request_body = {
        "input": {
            "bounds": {
                "bbox": BBOX
            },
            "data": [
                {
                    "type": "sentinel-1-grd",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{date}T00:00:00Z",
                            "to": f"{date}T23:59:59Z"
                        },
                        "orbitDirection": "DESCENDING"
                    },
                    "processing": {
                        "orthorectify": "true",
                        "demInstance": "COPERNICUS_30"
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

    print(
        f"{date} {polarization} -> "
        f"HTTP {response.status_code}"
    )

    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(
        f"Saved: {output_path} "
        f"({len(response.content)} bytes)"
    )


def main():

    token = get_token()
    print("OAuth: OK")

    for file_date, actual_date in DATES.items():

        for polarization in ["VV", "VH"]:

            output_path = (
                f"data/raw/"
                f"sentinel1_{file_date}_{polarization}.tif"
            )

            download_sentinel1(
                token,
                actual_date,
                polarization,
                output_path
            )


if __name__ == "__main__":
    main()