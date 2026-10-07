import rasterio
import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import label
from rasterio.warp import reproject, Resampling


VV_CHANGE = "outputs/event_vv_change_filtered.tif"
VH_CHANGE = "outputs/event_vh_change_filtered.tif"
SLOPE = "outputs/dem_slope.tif"



# Read SAR change layers


with rasterio.open(VV_CHANGE) as src:

    vv = src.read(1)
    sar_profile = src.profile.copy()
    sar_transform = src.transform
    sar_crs = src.crs
    sar_height = src.height
    sar_width = src.width


with rasterio.open(VH_CHANGE) as src:

    vh = src.read(1)



# Read slope


with rasterio.open(SLOPE) as src:

    slope_source = src.read(1)
    slope_transform = src.transform
    slope_crs = src.crs


print("VV shape:", vv.shape)
print("VH shape:", vh.shape)
print("Original slope shape:", slope_source.shape)



# Resample slope to Sentinel-1 grid


slope = np.empty(
    (sar_height, sar_width),
    dtype=np.float32
)


reproject(
    source=slope_source,
    destination=slope,
    src_transform=slope_transform,
    src_crs=slope_crs,
    dst_transform=sar_transform,
    dst_crs=sar_crs,
    resampling=Resampling.bilinear
)


print("Resampled slope shape:", slope.shape)



# Valid pixels


valid = (
    np.isfinite(vv) &
    np.isfinite(vh) &
    np.isfinite(slope)
)



# Candidate flood signal


radar_change = (
    (vv <= -1.5) &
    (vh <= -1.0)
)


terrain_constraint = (
    slope <= 20
)


candidate = (
    valid &
    radar_change &
    terrain_constraint
)


print()
print("Valid pixels:", valid.sum())

print(
    "Radar candidates:",
    radar_change.sum()
)

print(
    "After terrain constraint:",
    candidate.sum()
)

print(
    "Candidate percentage:",
    candidate.sum() / valid.sum() * 100,
    "%"
)



# Connected component filtering


candidate_uint8 = candidate.astype(
    np.uint8
)


components, num_components = label(
    candidate_uint8
)


sizes = np.bincount(
    components.ravel()
)


min_pixels = 20


clean_candidate = np.zeros_like(
    candidate,
    dtype=bool
)


for component_id in range(
    1,
    num_components + 1
):

    if sizes[component_id] >= min_pixels:

        clean_candidate[
            components == component_id
        ] = True


print(
    "After connected-component filtering:",
    clean_candidate.sum()
)



# Save candidate mask


sar_profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="lzw"
)


output_tif = (
    "outputs/event_flood_candidate.tif"
)


with rasterio.open(
    output_tif,
    "w",
    **sar_profile
) as dst:

    dst.write(
        clean_candidate.astype(
            np.uint8
        ),
        1
    )



# Visualization


plt.figure(
    figsize=(9, 8)
)


plt.imshow(
    clean_candidate,
    cmap="gray"
)


plt.title(
    "Candidate Flood Areas\n"
    "SAR Change + Terrain Constraint",
    fontsize=15,
    pad=12
)


plt.xticks([])
plt.yticks([])


plt.tight_layout()


output_png = (
    "outputs/event_flood_candidate.png"
)


plt.savefig(
    output_png,
    dpi=200,
    bbox_inches="tight"
)


plt.show()


print()
print("Saved:", output_tif)
print("Saved:", output_png)