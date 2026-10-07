import rasterio
import numpy as np
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt

before_files = {
    "VV": "data/raw/sentinel1_20260816_VV_utm.tif",
    "VH": "data/raw/sentinel1_20260816_VH_utm.tif"
}

after_files = {
    "VV": "data/raw/sentinel1_20260828_VV_utm.tif",
    "VH": "data/raw/sentinel1_20260828_VH_utm.tif"
}

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for i, name in enumerate(["VV", "VH"]):
    with rasterio.open(before_files[name]) as src:
        before = src.read(1).astype(float)

    with rasterio.open(after_files[name]) as src:
        after = src.read(1).astype(float)

    before[before <= 0] = np.nan
    after[after <= 0] = np.nan

    before_db = 10 * np.log10(before)
    after_db = 10 * np.log10(after)

    change = after_db - before_db
    change_filtered = median_filter(change, size=5)

    image = axes[i].imshow(
        change_filtered,
        cmap="RdBu_r",
        vmin=-6,
        vmax=6
    )

    axes[i].set_title(f"{name} UTM Change")
    axes[i].set_axis_off()

    fig.colorbar(image, ax=axes[i], label="dB change")

plt.tight_layout()
plt.savefig(
    "outputs/utm_sar_change_comparison.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("Saved: outputs/utm_sar_change_comparison.png")