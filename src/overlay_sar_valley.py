import rasterio
import numpy as np
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt

before_path = "data/raw/sentinel1_20260816_VV_utm.tif"
after_path = "data/raw/sentinel1_20260828_VV_utm.tif"
corridor_path = "outputs/valley_corridor.tif"

with rasterio.open(before_path) as src:
    before = src.read(1).astype(float)

with rasterio.open(after_path) as src:
    after = src.read(1).astype(float)

with rasterio.open(corridor_path) as src:
    corridor = src.read(1).astype(bool)

before[before <= 0] = np.nan
after[after <= 0] = np.nan

before_db = 10 * np.log10(before)
after_db = 10 * np.log10(after)

change = after_db - before_db
change_filtered = median_filter(change, size=5)

negative_change = np.where(
    corridor & (change_filtered <= -1.0),
    change_filtered,
    np.nan
)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

im1 = axes[0].imshow(
    change_filtered,
    cmap="RdBu_r",
    vmin=-6,
    vmax=6
)

axes[0].set_title("VV SAR Change")
axes[0].set_axis_off()

fig.colorbar(
    im1,
    ax=axes[0],
    label="dB change"
)

im2 = axes[1].imshow(
    negative_change,
    cmap="Blues",
    vmin=-6,
    vmax=0
)

axes[1].set_title(
    "Negative SAR Change Inside Valley Corridor"
)

axes[1].set_axis_off()

fig.colorbar(
    im2,
    ax=axes[1],
    label="dB decrease"
)

plt.tight_layout()

plt.savefig(
    "outputs/sar_valley_overlay.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

valid_corridor = corridor & np.isfinite(change_filtered)

negative_pixels = np.sum(
    valid_corridor & (change_filtered <= -1.0)
)

corridor_pixels = np.sum(valid_corridor)

print(f"Valid corridor pixels: {corridor_pixels}")
print(f"Negative-change pixels: {negative_pixels}")

if corridor_pixels > 0:
    percentage = negative_pixels / corridor_pixels * 100
    print(f"Negative-change percentage: {percentage:.2f}%")

print("Saved: outputs/sar_valley_overlay.png")