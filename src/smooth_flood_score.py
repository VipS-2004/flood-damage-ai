import rasterio
import numpy as np
from scipy.ndimage import median_filter

INPUT = "outputs/event_flood_score.tif"
OUTPUT = "outputs/event_flood_score_smoothed.tif"

with rasterio.open(INPUT) as src:
    score = src.read(1)
    profile = src.profile.copy()

smoothed = median_filter(score, size=9)

profile.update(
    dtype="float32",
    count=1,
    compress="lzw",
)

with rasterio.open(OUTPUT, "w", **profile) as dst:
    dst.write(smoothed.astype(np.float32), 1)

print("Saved:", OUTPUT)