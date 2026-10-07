import rasterio
import numpy as np
import matplotlib.pyplot as plt

VV_PATH = "data/raw/sentinel1_20260828_VV.tif"
MASK_PATH = "outputs/event_flood_candidate_v2.tif"
OUTPUT = "outputs/event_flood_candidate_overlay.png"

with rasterio.open(VV_PATH) as src:
    vv = src.read(1).astype(np.float32)

with rasterio.open(MASK_PATH) as src:
    mask = src.read(1)

vv_db = np.full_like(vv, np.nan)

valid = vv > 0
vv_db[valid] = 10 * np.log10(vv[valid])

low = np.nanpercentile(vv_db, 2)
high = np.nanpercentile(vv_db, 98)

plt.figure(figsize=(12, 8))

plt.imshow(
    vv_db,
    cmap="gray",
    vmin=low,
    vmax=high,
)

overlay = np.ma.masked_where(mask == 0, mask)

plt.imshow(
    overlay,
    cmap="autumn",
    alpha=0.8,
)

plt.title("After-event Sentinel-1 with Candidate Flood Mask")
plt.axis("off")
plt.tight_layout()

plt.savefig(
    OUTPUT,
    dpi=150,
    bbox_inches="tight",
)

print("Saved:", OUTPUT)