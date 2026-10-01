import requests
from shapely.geometry import shape, box

STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"

# Our broad test AOI
AOI = box(
    84.41, 27.71,
    85.41, 28.31
)

payload = {
    "collections": ["sentinel-1-grd"],
    "bbox": [84.41, 27.71, 85.41, 28.31],
    "datetime": "2026-08-10T00:00:00Z/2026-09-10T23:59:59Z",
    "limit": 100
}

response = requests.post(
    STAC_URL,
    json=payload,
    timeout=30
)

response.raise_for_status()

features = response.json()["features"]

selected = []

for feature in features:

    props = feature["properties"]

    orbit = props.get("sat:relative_orbit")
    direction = props.get("sat:orbit_state")

    if orbit == 121 and direction == "descending":

        footprint = shape(feature["geometry"])

        selected.append({
            "date": props["datetime"],
            "footprint": footprint
        })


selected.sort(key=lambda x: x["date"])

print("Selected scenes:")
for scene in selected:
    print(scene["date"])

print()

# Get the common footprint of the two scenes
common_footprint = selected[0]["footprint"]

for scene in selected[1:]:
    common_footprint = common_footprint.intersection(
        scene["footprint"]
    )

# Intersect with our requested AOI
valid_area = common_footprint.intersection(AOI)

print("Common Sentinel-1 footprint bounds:")
print(common_footprint.bounds)

print()

print("Valid intersection with current AOI:")
print(valid_area.bounds)

print()

print("Valid area:", valid_area.area)