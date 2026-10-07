import numpy as np
import rasterio

CORRIDOR = "outputs/drainage_corridor_100m.tif"

PAIRS = {
    "VV": (
        "data/processed/sentinel1_20260816_VV_gamma0terrain_utm_aligned.tif",
        "data/processed/sentinel1_20260828_VV_gamma0terrain_utm_aligned.tif",
    ),
    "VH": (
        "data/processed/sentinel1_20260816_VH_gamma0terrain_utm_aligned.tif",
        "data/processed/sentinel1_20260828_VH_gamma0terrain_utm_aligned.tif",
    ),
}


def to_db(data):
    result = np.full(data.shape, np.nan, dtype=np.float32)
    valid = np.isfinite(data) & (data > 0)
    result[valid] = 10 * np.log10(data[valid])
    return result


with rasterio.open(CORRIDOR) as src:
    corridor = src.read(1) == 1

print(f"Corridor pixels: {corridor.sum():,}")

for band, (before_file, after_file) in PAIRS.items():
    with rasterio.open(before_file) as src:
        before = src.read(1)

    with rasterio.open(after_file) as src:
        after = src.read(1)

    before_db = to_db(before)
    after_db = to_db(after)

    change = after_db - before_db

    valid = corridor & np.isfinite(change)
    values = change[valid]

    print(f"\n{band}")
    print(f"Valid corridor pixels: {len(values):,}")
    print(f"Median change: {np.median(values):.3f} dB")
    print(f"P05: {np.percentile(values, 5):.3f} dB")
    print(f"P10: {np.percentile(values, 10):.3f} dB")
    print(f"P25: {np.percentile(values, 25):.3f} dB")
    print(f"P75: {np.percentile(values, 75):.3f} dB")
    print(f"P90: {np.percentile(values, 90):.3f} dB")
    print(f"P95: {np.percentile(values, 95):.3f} dB")

    for threshold in [-1, -2, -3, -4]:
        count = np.sum(values <= threshold)
        percentage = 100 * count / len(values)
        print(
            f"Change <= {threshold:+.0f} dB: "
            f"{count:,} pixels ({percentage:.2f}%)"
        )