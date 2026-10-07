import numpy as np
import rasterio
from scipy.ndimage import label

CORRIDOR = "outputs/drainage_corridor_100m.tif"

VV_BEFORE = "data/processed/sentinel1_20260816_VV_gamma0terrain_utm_aligned.tif"
VV_AFTER = "data/processed/sentinel1_20260828_VV_gamma0terrain_utm_aligned.tif"

VH_BEFORE = "data/processed/sentinel1_20260816_VH_gamma0terrain_utm_aligned.tif"
VH_AFTER = "data/processed/sentinel1_20260828_VH_gamma0terrain_utm_aligned.tif"

THRESHOLD = -2.0


def to_db(data):
    result = np.full(data.shape, np.nan, dtype=np.float32)
    valid = np.isfinite(data) & (data > 0)
    result[valid] = 10 * np.log10(data[valid])
    return result


with rasterio.open(CORRIDOR) as src:
    corridor = src.read(1) == 1
    profile = src.profile.copy()

with rasterio.open(VV_BEFORE) as src:
    vv_before = src.read(1)

with rasterio.open(VV_AFTER) as src:
    vv_after = src.read(1)

with rasterio.open(VH_BEFORE) as src:
    vh_before = src.read(1)

with rasterio.open(VH_AFTER) as src:
    vh_after = src.read(1)

vv_change = to_db(vv_after) - to_db(vv_before)
vh_change = to_db(vh_after) - to_db(vh_before)

valid = (
    corridor
    & np.isfinite(vv_change)
    & np.isfinite(vh_change)
)

joint = (
    valid
    & (vv_change <= THRESHOLD)
    & (vh_change <= THRESHOLD)
)

print(f"Corridor pixels: {corridor.sum():,}")
print(f"Valid pixels: {valid.sum():,}")
print(f"Joint VV/VH <= {THRESHOLD:.1f} dB: {joint.sum():,}")

percentage = 100 * joint.sum() / valid.sum()
print(f"Joint percentage: {percentage:.2f}%")

labels, count = label(joint)

sizes = np.bincount(labels.ravel())[1:]
sizes = np.sort(sizes)[::-1]

print(f"Connected components: {count}")

print("\nLargest joint-evidence components:")

for i, size in enumerate(sizes[:20], start=1):
    area_ha = size * abs(profile["transform"].a * profile["transform"].e) / 10000
    print(
        f"{i:2d}. "
        f"{size:6d} pixels | "
        f"{area_ha:7.2f} ha"
    )

output = joint.astype(np.uint8)

profile.update(
    dtype="uint8",
    count=1,
    nodata=0
)

output_file = "outputs/joint_sar_evidence.tif"

with rasterio.open(output_file, "w", **profile) as dst:
    dst.write(output, 1)

print(f"\nSaved: {output_file}")