import requests
from shapely.geometry import shape, box


STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"

EVENT_AOI = [
    85.28,
    28.10,
    85.60,
    28.34
]

START_DATE = "2026-08-24"
END_DATE = "2026-09-02"


aoi = box(*EVENT_AOI)


payload = {
    "collections": ["sentinel-2-l2a"],
    "bbox": EVENT_AOI,
    "datetime": (
        f"{START_DATE}T00:00:00Z/"
        f"{END_DATE}T23:59:59Z"
    ),
    "limit": 100
}


print("Searching Copernicus Sentinel-2...")
print()


response = requests.post(
    STAC_URL,
    json=payload,
    timeout=30
)

response.raise_for_status()

features = response.json()["features"]

print("Scenes returned:", len(features))
print()


scenes = []


for feature in features:

    props = feature["properties"]

    footprint = shape(feature["geometry"])

    intersection = footprint.intersection(aoi)

    coverage = (
        intersection.area /
        aoi.area *
        100
    )

    if coverage < 95:
        continue

    date = props["datetime"][:10]

    cloud = props.get(
        "eo:cloud_cover"
    )

    scenes.append({
        "date": date,
        "cloud": cloud,
        "coverage": coverage,
        "id": feature["id"]
    })


scenes.sort(
    key=lambda x: (
        x["cloud"] if x["cloud"] is not None else 999,
        x["date"]
    )
)


print("Sentinel-2 scenes covering at least 95% of AOI:")
print()


for scene in scenes:

    print(
        scene["date"],
        "| cloud:",
        scene["cloud"],
        "%",
        "| coverage:",
        round(scene["coverage"], 1),
        "%"
    )

    print(
        "  ID:",
        scene["id"]
    )

    print()


print(
    "Total suitable scenes:",
    len(scenes)
)