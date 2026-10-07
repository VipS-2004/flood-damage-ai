import rasterio
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage



# INPUT FILES


before_file = "data/processed/sentinel1_20260816_VV_utm.tif"
after_file = "data/processed/sentinel1_20260828_VV_utm.tif"

output = "outputs/flood_mask_analysis.png"



# READ REPROJECTED DATA


with rasterio.open(before_file) as src:

    before = src.read(1).astype(np.float32)

    transform = src.transform
    crs = src.crs

    pixel_width = abs(transform.a)
    pixel_height = abs(transform.e)


with rasterio.open(after_file) as src:

    after = src.read(1).astype(np.float32)



# VERIFY ALIGNMENT


if before.shape != after.shape:
    raise ValueError(
        f"Shape mismatch: "
        f"{before.shape} vs {after.shape}"
    )



# CONVERT TO dB


def to_db(data):

    data = data.copy()

    data[data <= 0] = np.nan

    return 10 * np.log10(data)


before_db = to_db(before)
after_db = to_db(after)



# VALID PIXELS


valid = (
    np.isfinite(before_db) &
    np.isfinite(after_db)
)



# SAR CHANGE
#
# Before - After
#
# Positive value = backscatter decreased


change_db = np.full_like(
    before_db,
    np.nan
)

change_db[valid] = (
    before_db[valid] -
    after_db[valid]
)



# FLOOD CANDIDATE


threshold = 3.0

flood_candidate = (
    valid &
    (change_db >= threshold)
)



# CONNECTED COMPONENT ANALYSIS


structure = np.ones(
    (3, 3),
    dtype=np.uint8
)

labeled, num_regions = ndimage.label(
    flood_candidate,
    structure=structure
)

print(
    "Initial candidate regions:",
    num_regions
)



# REMOVE SMALL REGIONS


min_pixels = 50

component_sizes = np.bincount(
    labeled.ravel()
)

clean_mask = np.zeros(
    flood_candidate.shape,
    dtype=bool
)

for region_id in range(
    1,
    len(component_sizes)
):

    size = component_sizes[region_id]

    if size >= min_pixels:

        clean_mask[
            labeled == region_id
        ] = True



# MORPHOLOGICAL CLEANING


clean_mask = ndimage.binary_opening(
    clean_mask,
    structure=structure
)

clean_mask = ndimage.binary_closing(
    clean_mask,
    structure=structure
)



# AREA CALCULATION


pixel_area_m2 = (
    pixel_width *
    pixel_height
)

flood_pixels = int(
    np.sum(clean_mask)
)

flood_area_m2 = (
    flood_pixels *
    pixel_area_m2
)

flood_area_hectares = (
    flood_area_m2 / 10_000
)

flood_area_km2 = (
    flood_area_m2 / 1_000_000
)



# RESULTS


print()
print("=" * 60)
print("SENTINEL-1 FLOOD ANALYSIS")
print("=" * 60)

print(f"CRS: {crs}")

print(
    f"Pixel size: "
    f"{pixel_width:.3f} × "
    f"{pixel_height:.3f} m"
)

print(
    f"Pixel area: "
    f"{pixel_area_m2:.2f} m²"
)

print(
    f"Flood threshold: "
    f"{threshold:.1f} dB"
)

print(
    f"Minimum region: "
    f"{min_pixels} pixels"
)

print(
    f"Flood pixels: "
    f"{flood_pixels:,}"
)

print(
    f"Flooded area: "
    f"{flood_area_m2:,.2f} m²"
)

print(
    f"Flooded area: "
    f"{flood_area_hectares:,.2f} hectares"
)

print(
    f"Flooded area: "
    f"{flood_area_km2:,.4f} km²"
)

print("=" * 60)



# VISUALIZATION


fig, axes = plt.subplots(
    1,
    2,
    figsize=(13, 6),
    constrained_layout=True
)


# ------------------------------------------------------------
# RAW CANDIDATE
# ------------------------------------------------------------

axes[0].imshow(
    flood_candidate,
    cmap="Blues"
)

axes[0].set_title(
    f"Raw Flood Candidate\n"
    f"VV decrease ≥ {threshold:.1f} dB",
    fontsize=14,
    fontweight="bold"
)

axes[0].set_xticks([])
axes[0].set_yticks([])


# ------------------------------------------------------------
# CLEANED MASK
# ------------------------------------------------------------

axes[1].imshow(
    clean_mask,
    cmap="Blues"
)

axes[1].set_title(
    f"Cleaned Flood Mask\n"
    f"Minimum region = {min_pixels} pixels",
    fontsize=14,
    fontweight="bold"
)

axes[1].set_xticks([])
axes[1].set_yticks([])



# TITLE


fig.suptitle(
    "Sentinel-1 Flood Mask Refinement | Nepal",
    fontsize=18,
    fontweight="bold"
)



# SAVE


plt.savefig(
    output,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved:", output)