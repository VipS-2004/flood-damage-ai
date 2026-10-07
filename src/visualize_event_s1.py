import rasterio
import numpy as np
import matplotlib.pyplot as plt

from scipy import ndimage



# FILES


before_file = "data/raw/sentinel1_20260816_VV.tif"
after_file  = "data/raw/sentinel1_20260828_VV.tif"

output = "outputs/nepal_flood_cleaned_mask.png"



# READ DATA


with rasterio.open(before_file) as src:

    before = src.read(1).astype(np.float32)

    # Pixel dimensions
    pixel_width = abs(src.transform.a)
    pixel_height = abs(src.transform.e)

    crs = src.crs


with rasterio.open(after_file) as src:

    after = src.read(1).astype(np.float32)



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


change_db = np.full_like(
    before_db,
    np.nan
)

change_db[valid] = (
    before_db[valid] - after_db[valid]
)



# INITIAL FLOOD THRESHOLD


threshold = 3.0

flood_candidate = (
    valid &
    (change_db >= threshold)
)



# REMOVE SMALL ISOLATED REGIONS


# 8-connected neighborhood
structure = np.ones((3, 3), dtype=np.uint8)


labeled, num_features = ndimage.label(
    flood_candidate,
    structure=structure
)



# REMOVE SMALL COMPONENTS


# Minimum connected component size
# Adjust depending on image resolution.

min_pixels = 50


component_sizes = np.bincount(
    labeled.ravel()
)


clean_mask = np.zeros_like(
    flood_candidate,
    dtype=bool
)


for component_id in range(
    1,
    len(component_sizes)
):

    size = component_sizes[component_id]

    if size >= min_pixels:

        clean_mask[
            labeled == component_id
        ] = True



# OPTIONAL MORPHOLOGICAL CLEANING


# Remove tiny holes / smooth mask

clean_mask = ndimage.binary_opening(
    clean_mask,
    structure=structure
)

clean_mask = ndimage.binary_closing(
    clean_mask,
    structure=structure
)



# FLOODED AREA


pixel_area_m2 = (
    pixel_width *
    pixel_height
)

flood_pixels = np.sum(clean_mask)

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



# PRINT RESULTS


print()
print("=" * 55)
print("NEPAL FLOOD SAR ANALYSIS")
print("=" * 55)

print(f"CRS: {crs}")

print(
    f"Pixel size: "
    f"{pixel_width:.2f} m × "
    f"{pixel_height:.2f} m"
)

print(
    f"Pixel area: "
    f"{pixel_area_m2:.2f} m²"
)

print(
    f"Threshold: "
    f"{threshold:.1f} dB"
)

print(
    f"Minimum component: "
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

print("=" * 55)



# DISPLAY MASK


fig, axes = plt.subplots(
    1,
    2,
    figsize=(13, 6),
    constrained_layout=True
)


# ------------------------------------------------------------
# Raw candidate
# ------------------------------------------------------------

axes[0].imshow(
    flood_candidate,
    cmap="Blues"
)

axes[0].set_title(
    "Raw Flood Candidate Mask\n"
    f"VV decrease ≥ {threshold:.1f} dB",
    fontsize=14,
    fontweight="bold"
)

axes[0].set_xticks([])
axes[0].set_yticks([])


# ------------------------------------------------------------
# Clean mask
# ------------------------------------------------------------

axes[1].imshow(
    clean_mask,
    cmap="Blues"
)

axes[1].set_title(
    "Cleaned Flood Mask\n"
    f"Minimum region = {min_pixels} pixels",
    fontsize=14,
    fontweight="bold"
)

axes[1].set_xticks([])
axes[1].set_yticks([])



# MAIN TITLE


fig.suptitle(
    "Sentinel-1 Flood Mask Refinement | Nepal",
    fontsize=19,
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