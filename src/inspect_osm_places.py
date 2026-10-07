import geopandas as gpd
import pandas as pd

settlements_path = "data/raw/osm_20260727/settlements.parquet"
hospitals_path = "data/raw/osm_20260727/hospitals.parquet"

settlements = gpd.read_parquet(settlements_path)
hospitals = gpd.read_parquet(hospitals_path)


def tags_to_dict(tags):
    if isinstance(tags, list):
        return dict(tags)
    return {}


settlement_rows = []

for _, row in settlements.iterrows():
    tags = tags_to_dict(row["tags"])

    settlement_rows.append({
        "osm_id": row["osm_id"],
        "name": tags.get("name"),
        "name_en": tags.get("name:en"),
        "place": tags.get("place"),
        "elevation": tags.get("ele"),
        "longitude": row["geom"].x,
        "latitude": row["geom"].y,
    })

settlement_df = pd.DataFrame(settlement_rows)

print("\nSettlement types:")
print(settlement_df["place"].value_counts())

print("\nSettlements:")
print(
    settlement_df[
        ["name", "name_en", "place", "elevation", "longitude", "latitude"]
    ].to_string(index=False)
)


hospital_rows = []

for _, row in hospitals.iterrows():
    tags = tags_to_dict(row["tags"])

    hospital_rows.append({
        "osm_id": row["osm_id"],
        "name": tags.get("name"),
        "amenity": tags.get("amenity"),
        "source": tags.get("source"),
        "longitude": row["geom"].x,
        "latitude": row["geom"].y,
    })

hospital_df = pd.DataFrame(hospital_rows)

print("\nHospitals:")
print(
    hospital_df[
        ["name", "amenity", "source", "longitude", "latitude"]
    ].to_string(index=False)
)