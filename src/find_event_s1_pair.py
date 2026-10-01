import requests
from shapely.geometry import shape, box
from datetime import date


STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"

EVENT_DATE = "2026-08-26"

EVENT_AOI = [
    85.28,
    28.10,
    85.60,
    28.34
]

START_DATE = "2026-08-01"
END_DATE = "2026-09-10"


# Create AOI rectangle
aoi = box(*EVENT_AOI)


# Search Sentinel-1 scenes
payload = {
    "collections": ["sentinel-1-grd"],
    "bbox": EVENT_AOI,
    "datetime": (
        f"{START_DATE}T00:00:00Z/"
        f"{END_DATE}T23:59:59Z"
    ),
    "limit": 100
}


print("Searching Copernicus Sentinel-1...")
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


# Store scenes covering our AOI
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

    # We want scenes covering almost the entire AOI
    if coverage < 95:
        continue

    date_value = props["datetime"][:10]

    orbit = props.get(
        "sat:relative_orbit"
    )

    direction = props.get(
        "sat:orbit_state"
    )

    scenes.append({
        "date": date_value,
        "orbit": orbit,
        "direction": direction,
        "coverage": coverage,
        "id": feature["id"]
    })


# Remove duplicates
unique = {}

for scene in scenes:

    key = (
        scene["date"],
        scene["orbit"],
        scene["direction"]
    )

    unique[key] = scene


scenes = list(unique.values())


# Sort chronologically
scenes.sort(
    key=lambda x: x["date"]
)


print("Scenes covering at least 95% of AOI:")
print()


for scene in scenes:

    print(
        scene["date"],
        "| orbit:",
        scene["orbit"],
        "|",
        scene["direction"],
        "| coverage:",
        round(scene["coverage"], 1),
        "%"
    )


# Find same-orbit before/after pairs
event = date.fromisoformat(EVENT_DATE)

pairs = []


for i, before in enumerate(scenes):

    before_date = date.fromisoformat(
        before["date"]
    )

    # Before scene must be before the event
    if before_date >= event:
        continue


    for after in scenes[i + 1:]:

        after_date = date.fromisoformat(
            after["date"]
        )

        # After scene must be after the event
        if after_date <= event:
            continue

        # Same relative orbit
        if before["orbit"] != after["orbit"]:
            continue

        # Same ascending/descending direction
        if before["direction"] != after["direction"]:
            continue


        days_before = (
            event - before_date
        ).days

        days_after = (
            after_date - event
        ).days

        interval = (
            after_date - before_date
        ).days


        pairs.append({
            "before": before,
            "after": after,
            "days_before": days_before,
            "days_after": days_after,
            "interval": interval
        })


# Prefer approximately 12-day pairs
pairs.sort(
    key=lambda p: (
        abs(p["interval"] - 12),
        p["days_after"]
    )
)


print()
print("Same-orbit before/after candidates:")
print()


if not pairs:

    print("No valid same-orbit pairs found.")

else:

    for pair in pairs:

        before = pair["before"]
        after = pair["after"]

        print(
            f'{before["date"]} -> '
            f'{after["date"]} | '
            f'orbit {before["orbit"]} | '
            f'{before["direction"]} | '
            f'{pair["interval"]} days | '
            f'{pair["days_before"]} days before | '
            f'{pair["days_after"]} days after'
        )