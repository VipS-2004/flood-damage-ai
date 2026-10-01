import rasterio
import numpy as np
import matplotlib.pyplot as plt

from scipy import ndimage


VV_CHANGE = "outputs/vv_change.tif"
VH_CHANGE = "outputs/vh_change.tif"
SLOPE = "outputs/dem_slope.tif"

OUTPUT = "outputs/flood_baseline_refined.png"


def read_raster(path):
    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32)



# Read layers


vv_change = read_raster(VV_CHANGE)
vh_change = read_raster(VH_CHANGE)
slope = read_raster(SLOPE)



# Valid pixels


valid = (
    np.isfinite(vv_change)
    &
    np.isfinite(vh_change)
    &
    np.isfinite(slope)
)



# Raw radar candidate


radar_candidate = (
    (vv_change <= -3.0)
    &
    (vh_change <= -2.0)
    &
    valid
)



# Terrain constraint

#
# Conservative baseline:
# keep areas with slope <= 15 degrees.
#
# This is a heuristic, not a universal flood rule.
#

terrain_candidate = slope <= 15.0


candidate = (
    radar_candidate
    &
    terrain_candidate
)



# Remove isolated pixels


# 3x3 morphological opening removes
# isolated/small speckle-like pixels.

candidate = ndimage.binary_opening(
    candidate,
    structure=np.ones((3, 3))
)



# Fill small gaps


candidate = ndimage.binary_closing(
    candidate,
    structure=np.ones((5, 5))
)



# Connected components


labels, num_features = ndimage.label(candidate)

component_sizes = np.bincount(
    labels.ravel()
)

# Keep components with at least 20 pixels
MIN_PIXELS = 20

large_components = (
    component_sizes >= MIN_PIXELS
)

large_components[0] = False

refined = large_components[labels]



# Statistics


total_valid = np.sum(valid)

raw_pixels = np.sum(radar_candidate)

terrain_pixels = np.sum(
    radar_candidate & terrain_candidate
)

refined_pixels = np.sum(refined)


print("Total valid pixels:", total_valid)

print(
    "Raw radar candidates:",
    raw_pixels
)

print(
    "After terrain constraint:",
    terrain_pixels
)

print(
    "After spatial filtering:",
    refined_pixels
)

print(
    "Final candidate percentage:",
    round(
        refined_pixels / total_valid * 100,
        2
    ),
    "%"
)

print(
    "Connected components:",
    num_features
)



# Visualization


fig, axes = plt.subplots(
    1,
    3,
    figsize=(15, 5)
)


axes[0].imshow(
    radar_candidate,
    cmap="gray"
)

axes[0].set_title(
    "Raw Radar Candidates"
)


axes[1].imshow(
    radar_candidate & terrain_candidate,
    cmap="gray"
)

axes[1].set_title(
    "After Terrain Constraint"
)


axes[2].imshow(
    refined,
    cmap="gray"
)

axes[2].set_title(
    "Refined Flood Candidates"
)


for ax in axes:
    ax.axis("off")


plt.tight_layout()

plt.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print("Saved:", OUTPUT)