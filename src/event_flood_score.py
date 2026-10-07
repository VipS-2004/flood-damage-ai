import rasterio
import numpy as np
import matplotlib.pyplot as plt


VV_CHANGE = "outputs/event_vv_change_filtered.tif"
VH_CHANGE = "outputs/event_vh_change_filtered.tif"
SLOPE = "outputs/dem_slope.tif"


with rasterio.open(VV_CHANGE) as src:
    vv = src.read(1)
    profile = src.profile.copy()
    transform = src.transform
    crs = src.crs
    height = src.height
    width = src.width


with rasterio.open(VH_CHANGE) as src:
    vh = src.read(1)


with rasterio.open(SLOPE) as src:
    slope_source = src.read(1)
    slope_transform = src.transform
    slope_crs = src.crs


from rasterio.warp import reproject, Resampling


slope = np.empty(
    (height, width),
    dtype=np.float32
)


reproject(
    source=slope_source,
    destination=slope,
    src_transform=slope_transform,
    src_crs=slope_crs,
    dst_transform=transform,
    dst_crs=crs,
    resampling=Resampling.bilinear
)


valid = (
    np.isfinite(vv) &
    np.isfinite(vh) &
    np.isfinite(slope)
)


vv_valid = vv[valid]
vh_valid = vh[valid]
slope_valid = slope[valid]


vv_low = np.percentile(vv_valid, 5)
vv_high = np.percentile(vv_valid, 50)

vh_low = np.percentile(vh_valid, 5)
vh_high = np.percentile(vh_valid, 50)


vv_score = np.zeros_like(vv, dtype=np.float32)
vh_score = np.zeros_like(vh, dtype=np.float32)
slope_score = np.zeros_like(slope, dtype=np.float32)


vv_score[valid] = np.clip(
    (vv_high - vv[valid]) /
    (vv_high - vv_low),
    0,
    1
)


vh_score[valid] = np.clip(
    (vh_high - vh[valid]) /
    (vh_high - vh_low),
    0,
    1
)


slope_score[valid] = np.clip(
    1 - slope[valid] / 30,
    0,
    1
)


flood_score = (
    0.45 * vv_score +
    0.45 * vh_score +
    0.10 * slope_score
)


flood_score[~valid] = np.nan


valid_scores = flood_score[
    np.isfinite(flood_score)
]


print("Valid pixels:", valid.sum())

print(
    "VV 5th percentile:",
    vv_low
)

print(
    "VV median:",
    vv_high
)

print(
    "VH 5th percentile:",
    vh_low
)

print(
    "VH median:",
    vh_high
)

print(
    "Flood score median:",
    np.percentile(valid_scores, 50)
)

print(
    "Flood score 90th percentile:",
    np.percentile(valid_scores, 90)
)

print(
    "Flood score 95th percentile:",
    np.percentile(valid_scores, 95)
)

print(
    "Flood score 99th percentile:",
    np.percentile(valid_scores, 99)
)


profile.update(
    dtype="float32",
    count=1,
    nodata=np.nan,
    compress="lzw"
)


output_tif = (
    "outputs/event_flood_score.tif"
)


with rasterio.open(
    output_tif,
    "w",
    **profile
) as dst:

    dst.write(
        flood_score.astype(np.float32),
        1
    )


plt.figure(
    figsize=(10, 8)
)


im = plt.imshow(
    flood_score,
    cmap="viridis",
    vmin=0,
    vmax=1
)


plt.title(
    "SAR Flood-Likelihood Score\n"
    "16 Aug → 28 Aug 2026",
    fontsize=15,
    pad=12
)


plt.xticks([])
plt.yticks([])


cbar = plt.colorbar(
    im,
    fraction=0.046,
    pad=0.03
)


cbar.set_label(
    "Flood score",
    fontsize=10
)


plt.tight_layout()


output_png = (
    "outputs/event_flood_score.png"
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