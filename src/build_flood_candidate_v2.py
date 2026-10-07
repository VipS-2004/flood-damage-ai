import rasterio
import numpy as np
from scipy.ndimage import label, binary_opening, binary_closing
from rasterio.warp import reproject, Resampling

SCORE_PATH = "outputs/event_flood_score_smoothed.tif"
SLOPE_PATH = "outputs/dem_slope.tif"

OUTPUT_MASK = "outputs/event_flood_candidate_v2.tif"
OUTPUT_PNG = "outputs/event_flood_candidate_v2.png"

SCORE_THRESHOLD = 0.65
SLOPE_THRESHOLD = 10.0
MIN_PIXELS = 50

with rasterio.open(SCORE_PATH) as src:
    score = src.read(1).astype(np.float32)
    score_profile = src.profile.copy()
    score_transform = src.transform
    score_crs = src.crs

with rasterio.open(SLOPE_PATH) as src:
    slope = src.read(1).astype(np.float32)
    slope_transform = src.transform
    slope_crs = src.crs

slope_resampled = np.empty_like(score, dtype=np.float32)

reproject(
    source=slope,
    destination=slope_resampled,
    src_transform=slope_transform,
    src_crs=slope_crs,
    dst_transform=score_transform,
    dst_crs=score_crs,
    resampling=Resampling.bilinear,
)

valid = np.isfinite(score) & np.isfinite(slope_resampled)

border = 30

valid[:border, :] = False
valid[-border:, :] = False
valid[:, :border] = False
valid[:, -border:] = False

candidate = (
    valid
    & (score >= SCORE_THRESHOLD)
    & (slope_resampled <= SLOPE_THRESHOLD)
)

structure = np.ones((3, 3), dtype=bool)

candidate = binary_opening(candidate, structure=structure)
candidate = binary_closing(candidate, structure=structure)

labels, num_components = label(candidate)

filtered = np.zeros_like(candidate, dtype=bool)

for component_id in range(1, num_components + 1):
    component_size = np.sum(labels == component_id)

    if component_size >= MIN_PIXELS:
        filtered[labels == component_id] = True

output = filtered.astype(np.uint8)

score_profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="lzw",
)

with rasterio.open(OUTPUT_MASK, "w", **score_profile) as dst:
    dst.write(output, 1)

print("Score threshold:", SCORE_THRESHOLD)
print("Slope threshold:", SLOPE_THRESHOLD)
print("Minimum component:", MIN_PIXELS, "pixels")
print("Initial candidate pixels:", int(candidate.sum()))
print("Final candidate pixels:", int(output.sum()))
print("Final candidate percentage:", output.mean() * 100)
print("Connected components:", num_components)
print("Saved:", OUTPUT_MASK)