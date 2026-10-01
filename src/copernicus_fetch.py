import requests


STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"



# TRISHULI CASE STUDY AOI


BBOX = [
    84.41,   # min longitude
    27.71,   # min latitude
    85.41,   # max longitude
    28.31    # max latitude
]



# FLOOD EVENT


EVENT_DATE = "2026-08-26"

START_DATE = "2026-08-10"
END_DATE = "2026-09-10"



# SEARCH


payload = {
    "collections": ["sentinel-1-grd"],
    "bbox": BBOX,
    "datetime": (
        f"{START_DATE}T00:00:00Z/"
        f"{END_DATE}T23:59:59Z"
    ),
    "limit": 100
}


response = requests.post(
    STAC_URL,
    json=payload,
    timeout=60
)

print("Status:", response.status_code)

response.raise_for_status()

data = response.json()

scenes = data.get("features", [])

from datetime import datetime


print("\nCANDIDATE SCENES")
print("=" * 80)


for scene in scenes:

    properties = scene.get("properties", {})

    date = properties.get("datetime", "")

    if date.startswith("2026-08-19") or date.startswith("2026-08-31"):

        print("\n" + "-" * 80)

        print("ID:")
        print(scene.get("id"))

        print("Date:")
        print(date)

        print("Relative orbit:")
        print(properties.get("sat:relative_orbit"))

        print("Orbit direction:")
        print(properties.get("sat:orbit_state"))

        print("Instrument mode:")
        print(properties.get("sar:instrument_mode"))

        print("\nBounding box:")
        print(scene.get("bbox"))

        print("\nAsset URLs:")

        for asset_name in ["vv", "vh"]:
           asset = scene.get("assets", {}).get(asset_name)

           if asset:
                print(
                    asset_name,
                    "→",
                    asset.get("href")
                )

print("\nNumber of scenes:", len(scenes))



# PRINT SCENE INFORMATION


for scene in scenes:

    properties = scene.get("properties", {})

    print("\n" + "=" * 70)

    print("ID:")
    print(scene.get("id"))

    print("Date:")
    print(properties.get("datetime"))

    print("Orbit direction:")
    print(properties.get("sat:orbit_state"))

    print("Relative orbit:")
    print(properties.get("sat:relative_orbit"))

    print("Instrument mode:")
    print(properties.get("sar:instrument_mode"))

    print("Polarization:")
    print(properties.get("s1:polarization"))