import rasterio
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage



# INPUT FILES


before_vv_file = (
    "data/processed/"
    "sentinel1_20260816_VV_utm.tif"
)

after_vv_file = (
    "data/processed/"
    "sentinel1_20260828_VV_utm.tif"
)

before_vh_file = (
    "data/processed/"
    "sentinel1_20260816_VH_utm.tif"
)

after_vh_file = (
    "data/processed/"
    "sentinel1_20260828_VH_utm.tif"
)


output = "outputs/vv_vh_flood_fusion.png"



# READ RASTER


def read_raster(filepath):

    with rasterio.open(filepath) as src:

        data = src.read(1).astype(np.float32)

        profile = src.profile.copy()

        transform = src.transform

        crs = src.crs

    return data, profile, transform, crs


before_vv, profile, transform, crs = read_raster(
    before_vv_file
)

after_vv, _, _, _ = read_raster(
    after_vv_file
)

before_vh, _, _, _ = read_raster(
    before_vh_file
)

after_vh, _, _, _ = read_raster(
    after_vh_file
)



# VERIFY SHAPES


shape = before_vv.shape

if (
    after_vv.shape != shape
    or before_vh.shape != shape
    or after_vh.shape != shape
):

    raise ValueError(
        "Input rasters do not have matching dimensions."
    )



# CONVERT TO dB


def to_db(data):

    data = data.copy()

    data[data <= 0] = np.nan

    return 10 * np.log10(data)


before_vv_db = to_db(before_vv)
after_vv_db = to_db(after_vv)

before_vh_db = to_db(before_vh)
after_vh_db = to_db(after_vh)



# VALID PIXELS


valid = (
    np.isfinite(before_vv_db)
    &
    np.isfinite(after_vv_db)
    &
    np.isfinite(before_vh_db)
    &
    np.isfinite(after_vh_db)
)



# CHANGE
#
# BEFORE - AFTER
#
# Positive = backscatter decreased


vv_change = np.full_like(
    before_vv_db,
    np.nan
)

vh_change = np.full_like(
    before_vh_db,
    np.nan
)


vv_change[valid] = (
    before_vv_db[valid]
    -
    after_vv_db[valid]
)

vh_change[valid] = (
    before_vh_db[valid]
    -
    after_vh_db[valid]
)



# THRESHOLDS


vv_threshold = 3.0
vh_threshold = 3.0



# INDIVIDUAL CANDIDATE MASKS


vv_mask = (
    valid
    &
    (vv_change >= vv_threshold)
)

vh_mask = (
    valid
    &
    (vh_change >= vh_threshold)
)



# VV + VH FUSION
#
# Pixel must satisfy BOTH conditions.


fusion_mask = (
    vv_mask
    &
    vh_mask
)



# CONNECTED COMPONENT ANALYSIS


structure = np.ones(
    (3, 3),
    dtype=np.uint8
)

labeled, num_regions = ndimage.label(
    fusion_mask,
    structure=structure
)


print(
    "Initial VV + VH regions:",
    num_regions
)



# REMOVE SMALL REGIONS


min_pixels = 50

component_sizes = np.bincount(
    labeled.ravel()
)

clean_mask = np.zeros(
    fusion_mask.shape,
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



# AREA


pixel_width = abs(transform.a)
pixel_height = abs(transform.e)

pixel_area = (
    pixel_width *
    pixel_height
)


flood_pixels = int(
    np.sum(clean_mask)
)


flood_area_m2 = (
    flood_pixels *
    pixel_area
)

flood_area_hectares = (
    flood_area_m2 / 10_000
)

flood_area_km2 = (
    flood_area_m2 / 1_000_000
)



# STATISTICS


total_valid_pixels = int(
    np.sum(valid)
)

vv_pixels = int(
    np.sum(vv_mask)
)

vh_pixels = int(
    np.sum(vh_mask)
)

fusion_pixels = int(
    np.sum(fusion_mask)
)


print()
print("=" * 65)
print("SENTINEL-1 VV + VH FLOOD FUSION")
print("=" * 65)

print(f"CRS: {crs}")

print(
    f"Pixel size: "
    f"{pixel_width:.3f} × "
    f"{pixel_height:.3f} m"
)

print(
    f"Pixel area: "
    f"{pixel_area:.2f} m²"
)

print()

print(
    f"VV threshold: "
    f"{vv_threshold:.1f} dB"
)

print(
    f"VH threshold: "
    f"{vh_threshold:.1f} dB"
)

print()

print(
    f"Valid pixels: "
    f"{total_valid_pixels:,}"
)

print(
    f"VV candidate pixels: "
    f"{vv_pixels:,}"
)

print(
    f"VH candidate pixels: "
    f"{vh_pixels:,}"
)

print(
    f"VV + VH candidate pixels: "
    f"{fusion_pixels:,}"
)

print()

print(
    f"Clean flood pixels: "
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
    f"{flood_area_km2:.4f} km²"
)

print("=" * 65)



# VISUALIZATION


fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 10),
    constrained_layout=True
)



# VV CHANGE


vv_limit = np.nanpercentile(
    np.abs(vv_change),
    98
)

im1 = axes[0, 0].imshow(
    vv_change,
    cmap="RdBu_r",
    vmin=-vv_limit,
    vmax=vv_limit
)

axes[0, 0].set_title(
    "VV Backscatter Change\nBefore − After",
    fontsize=14,
    fontweight="bold"
)

axes[0, 0].set_xticks([])
axes[0, 0].set_yticks([])

cbar1 = fig.colorbar(
    im1,
    ax=axes[0, 0],
    fraction=0.046,
    pad=0.03
)

cbar1.set_label(
    "VV Change (dB)"
)



# VH CHANGE


vh_limit = np.nanpercentile(
    np.abs(vh_change),
    98
)

im2 = axes[0, 1].imshow(
    vh_change,
    cmap="RdBu_r",
    vmin=-vh_limit,
    vmax=vh_limit
)

axes[0, 1].set_title(
    "VH Backscatter Change\nBefore − After",
    fontsize=14,
    fontweight="bold"
)

axes[0, 1].set_xticks([])
axes[0, 1].set_yticks([])

cbar2 = fig.colorbar(
    im2,
    ax=axes[0, 1],
    fraction=0.046,
    pad=0.03
)

cbar2.set_label(
    "VH Change (dB)"
)



# VV + VH RAW FUSION


axes[1, 0].imshow(
    fusion_mask,
    cmap="Blues"
)

axes[1, 0].set_title(
    "VV + VH Candidate Mask\n"
    "Both channels ≥ 3 dB decrease",
    fontsize=14,
    fontweight="bold"
)

axes[1, 0].set_xticks([])
axes[1, 0].set_yticks([])



# CLEAN FUSION MASK


axes[1, 1].imshow(
    clean_mask,
    cmap="Blues"
)

axes[1, 1].set_title(
    "Cleaned VV + VH Flood Mask\n"
    f"{flood_area_km2:.4f} km² candidate area",
    fontsize=14,
    fontweight="bold"
)

axes[1, 1].set_xticks([])
axes[1, 1].set_yticks([])



# MAIN TITLE


fig.suptitle(
    "Sentinel-1 Multi-Polarization Flood Detection | Nepal",
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