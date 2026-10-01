import rasterio
import numpy as np
import matplotlib.pyplot as plt



# Input files


BEFORE_VV = "data/raw/sentinel1_20260819_VV.tif"
AFTER_VV = "data/raw/sentinel1_20260831_VV.tif"

BEFORE_VH = "data/raw/sentinel1_20260819_VH.tif"
AFTER_VH = "data/raw/sentinel1_20260831_VH.tif"



# Output files


OUTPUT_MASK = "outputs/flood_baseline.png"

VV_CHANGE_OUTPUT = "outputs/vv_change.tif"
VH_CHANGE_OUTPUT = "outputs/vh_change.tif"



# Read raster


def read_raster(path):

    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32)



# Convert Sentinel-1 linear backscatter to dB


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



# Read Sentinel-1 data


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



# Calculate radar change


vv_change = (
    after_vv -
    before_vv
)

vh_change = (
    after_vh -
    before_vh
)



# Create valid pixel mask


valid = (
    np.isfinite(vv_change)
    &
    np.isfinite(vh_change)
)



# Initial flood candidate rule

#
# Potential inundation can produce a decrease
# in radar backscatter.
#
# Initial baseline:
#
# VV decrease <= -3 dB
# VH decrease <= -2 dB
#
# These are heuristic starting thresholds,
# not validated flood thresholds.


flood_candidate = (
    (vv_change <= -3.0)
    &
    (vh_change <= -2.0)
    &
    valid
)



# Statistics


total_valid = np.sum(valid)

flood_pixels = np.sum(
    flood_candidate
)

percentage = (
    flood_pixels /
    total_valid *
    100
)


print(
    "Valid pixels:",
    total_valid
)

print(
    "Flood candidate pixels:",
    flood_pixels
)

print(
    "Candidate percentage:",
    round(percentage, 2),
    "%"
)



# Save VV/VH change maps as GeoTIFF


with rasterio.open(BEFORE_VV) as src:

    profile = src.profile.copy()


profile.update(
    dtype="float32",
    count=1,
    compress="lzw",
    nodata=np.nan
)


with rasterio.open(
    VV_CHANGE_OUTPUT,
    "w",
    **profile
) as dst:

    dst.write(
        vv_change.astype(np.float32),
        1
    )


with rasterio.open(
    VH_CHANGE_OUTPUT,
    "w",
    **profile
) as dst:

    dst.write(
        vh_change.astype(np.float32),
        1
    )


print(
    "Saved:",
    VV_CHANGE_OUTPUT
)

print(
    "Saved:",
    VH_CHANGE_OUTPUT
)



# Visualization


fig, axes = plt.subplots(
    1,
    3,
    figsize=(15, 5)
)


# VV change

axes[0].imshow(
    vv_change,
    cmap="RdBu_r",
    vmin=-10,
    vmax=10
)

axes[0].set_title(
    "VV Change (dB)"
)


# VH change

axes[1].imshow(
    vh_change,
    cmap="RdBu_r",
    vmin=-10,
    vmax=10
)

axes[1].set_title(
    "VH Change (dB)"
)


# Flood candidates

axes[2].imshow(
    flood_candidate,
    cmap="gray"
)

axes[2].set_title(
    "Baseline Flood Candidates"
)


# Remove axes

for ax in axes:

    ax.axis("off")


plt.tight_layout()



# Save figure


plt.savefig(
    OUTPUT_MASK,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


print(
    "Saved:",
    OUTPUT_MASK
)