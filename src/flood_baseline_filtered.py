import rasterio
import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import median_filter



# Input files


BEFORE_VV = "data/raw/sentinel1_20260819_VV.tif"
AFTER_VV = "data/raw/sentinel1_20260831_VV.tif"

BEFORE_VH = "data/raw/sentinel1_20260819_VH.tif"
AFTER_VH = "data/raw/sentinel1_20260831_VH.tif"

SLOPE = "outputs/dem_slope.tif"



# Output


OUTPUT = "outputs/flood_baseline_filtered.png"



# Read raster


def read_raster(path):

    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32)



# Convert linear backscatter to dB


def to_db(image):

    result = np.full_like(
        image,
        np.nan,
        dtype=np.float32
    )

    valid = image > 0

    result[valid] = (
        10 * np.log10(image[valid])
    )

    return result



# Median filter while preserving NaN pixels


def speckle_filter(image, size=5):

    valid = np.isfinite(image)

    # Replace NaN temporarily
    filled = np.where(
        valid,
        image,
        0
    )

    filtered = median_filter(
        filled,
        size=size
    )

    return filtered



# Read data


before_vv = to_db(
    read_raster(BEFORE_VV)
)

after_vv = to_db(
    read_raster(AFTER_VV)
)

before_vh = to_db(
    read_raster(BEFORE_VH)
)

after_vh = to_db(
    read_raster(AFTER_VH)
)

slope = read_raster(SLOPE)



# Apply speckle reduction


before_vv_filtered = speckle_filter(
    before_vv,
    size=5
)

after_vv_filtered = speckle_filter(
    after_vv,
    size=5
)

before_vh_filtered = speckle_filter(
    before_vh,
    size=5
)

after_vh_filtered = speckle_filter(
    after_vh,
    size=5
)



# Calculate change


vv_change = (
    after_vv_filtered -
    before_vv_filtered
)

vh_change = (
    after_vh_filtered -
    before_vh_filtered
)



# Valid pixels


valid = (
    np.isfinite(vv_change)
    &
    np.isfinite(vh_change)
    &
    np.isfinite(slope)
)



# Radar candidate


radar_candidate = (
    (vv_change <= -3.0)
    &
    (vh_change <= -2.0)
    &
    valid
)



# Terrain constraint


terrain_candidate = (
    slope <= 15.0
)


candidate = (
    radar_candidate
    &
    terrain_candidate
)



# Statistics


total_valid = np.sum(valid)

radar_pixels = np.sum(
    radar_candidate
)

terrain_pixels = np.sum(
    candidate
)


print(
    "Total valid pixels:",
    total_valid
)

print(
    "Radar candidates:",
    radar_pixels
)

print(
    "After terrain constraint:",
    terrain_pixels
)

print(
    "Candidate percentage:",
    round(
        terrain_pixels /
        total_valid *
        100,
        2
    ),
    "%"
)



# Visualization


fig, axes = plt.subplots(
    2,
    3,
    figsize=(15, 9)
)


axes[0, 0].imshow(
    before_vv_filtered,
    cmap="gray"
)

axes[0, 0].set_title(
    "Filtered Before VV"
)


axes[0, 1].imshow(
    after_vv_filtered,
    cmap="gray"
)

axes[0, 1].set_title(
    "Filtered After VV"
)


axes[0, 2].imshow(
    vv_change,
    cmap="RdBu_r",
    vmin=-6,
    vmax=6
)

axes[0, 2].set_title(
    "Filtered VV Change"
)


axes[1, 0].imshow(
    before_vh_filtered,
    cmap="gray"
)

axes[1, 0].set_title(
    "Filtered Before VH"
)


axes[1, 1].imshow(
    after_vh_filtered,
    cmap="gray"
)

axes[1, 1].set_title(
    "Filtered After VH"
)


axes[1, 2].imshow(
    candidate,
    cmap="gray"
)

axes[1, 2].set_title(
    "Flood Candidates"
)


for ax in axes.flat:
    ax.axis("off")


plt.tight_layout()

plt.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


print(
    "Saved:",
    OUTPUT
)