import rasterio
import numpy as np
from scipy.ndimage import binary_opening, binary_closing, label
from rasterio.warp import reproject, Resampling


VV_BEFORE = "data/raw/sentinel1_20260816_VV.tif"
VH_BEFORE = "data/raw/sentinel1_20260816_VH.tif"

VV_AFTER = "data/raw/sentinel1_20260828_VV.tif"
VH_AFTER = "data/raw/sentinel1_20260828_VH.tif"

SLOPE_FILE = "outputs/dem_slope.tif"

OUTPUT_MASK = "outputs/event_flood_candidate_v3.tif"


def to_db(data):
    data = data.astype(np.float32)
    data[data <= 0] = np.nan
    return 10.0 * np.log10(data)


def read_raster(path):
    with rasterio.open(path) as src:
        data = src.read(1)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs

    return data, profile, transform, crs


vv_before_raw, profile, transform, crs = read_raster(VV_BEFORE)
vh_before_raw, _, vh_before_transform, vh_before_crs = read_raster(VH_BEFORE)
vv_after_raw, _, vv_after_transform, vv_after_crs = read_raster(VV_AFTER)
vh_after_raw, _, vh_after_transform, vh_after_crs = read_raster(VH_AFTER)

print("Reference raster")
print("Shape:", vv_before_raw.shape)
print("CRS:", crs)
print("Transform:", transform)

print()
print("Checking Sentinel-1 alignment")

rasters = {
    "VH before": (vh_before_raw, vh_before_transform, vh_before_crs),
    "VV after": (vv_after_raw, vv_after_transform, vv_after_crs),
    "VH after": (vh_after_raw, vh_after_transform, vh_after_crs),
}

for name, (data, raster_transform, raster_crs) in rasters.items():
    print(
        name,
        "| shape:", data.shape,
        "| CRS:", raster_crs,
        "| same shape:", data.shape == vv_before_raw.shape,
        "| same CRS:", raster_crs == crs,
        "| same transform:", raster_transform == transform,
    )

if not (
    vv_before_raw.shape
    == vh_before_raw.shape
    == vv_after_raw.shape
    == vh_after_raw.shape
):
    raise ValueError("Sentinel-1 rasters have different dimensions.")

if not (
    vh_before_crs == crs
    and vv_after_crs == crs
    and vh_after_crs == crs
):
    raise ValueError("Sentinel-1 rasters have different CRS.")

if not (
    vh_before_transform == transform
    and vv_after_transform == transform
    and vh_after_transform == transform
):
    raise ValueError("Sentinel-1 rasters have different transforms.")


vv_before = to_db(vv_before_raw)
vh_before = to_db(vh_before_raw)
vv_after = to_db(vv_after_raw)
vh_after = to_db(vh_after_raw)

print()
print("Post-event backscatter statistics")

for name, data in [
    ("VV", vv_after),
    ("VH", vh_after),
]:
    print(
        name,
        "| p1:", np.nanpercentile(data, 1),
        "| p5:", np.nanpercentile(data, 5),
        "| p10:", np.nanpercentile(data, 10),
        "| median:", np.nanmedian(data),
        "| p95:", np.nanpercentile(data, 95),
    )


vv_change = vv_after - vv_before
vh_change = vh_after - vh_before

print()
print("Pre/post change statistics")

for name, data in [
    ("VV change", vv_change),
    ("VH change", vh_change),
]:
    print(
        name,
        "| p1:", np.nanpercentile(data, 1),
        "| p5:", np.nanpercentile(data, 5),
        "| median:", np.nanmedian(data),
        "| p95:", np.nanpercentile(data, 95),
        "| p99:", np.nanpercentile(data, 99),
    )


with rasterio.open(SLOPE_FILE) as src:
    slope_raw = src.read(1)
    slope_transform = src.transform
    slope_crs = src.crs

slope = np.full(
    vv_before.shape,
    np.nan,
    dtype=np.float32,
)

reproject(
    source=slope_raw,
    destination=slope,
    src_transform=slope_transform,
    src_crs=slope_crs,
    dst_transform=transform,
    dst_crs=crs,
    dst_shape=vv_before.shape,
    resampling=Resampling.bilinear,
)

print()
print("Slope")
print("Source CRS:", slope_crs)
print("Target CRS:", crs)
print("Min:", np.nanmin(slope))
print("Median:", np.nanmedian(slope))
print("Max:", np.nanmax(slope))


valid = (
    np.isfinite(vv_before)
    & np.isfinite(vh_before)
    & np.isfinite(vv_after)
    & np.isfinite(vh_after)
    & np.isfinite(vv_change)
    & np.isfinite(vh_change)
    & np.isfinite(slope)
)

print()
print("Valid pixels:", valid.sum())


LOW_VV_THRESHOLD = -15.0
LOW_VH_THRESHOLD = -20.0
VV_CHANGE_THRESHOLD = -1.0
VH_CHANGE_THRESHOLD = -1.0
SLOPE_THRESHOLD = 20.0
MINIMUM_PIXELS = 1


low_vv = vv_after < LOW_VV_THRESHOLD
low_vh = vh_after < LOW_VH_THRESHOLD

vv_drop = vv_change < VV_CHANGE_THRESHOLD
vh_drop = vh_change < VH_CHANGE_THRESHOLD

gentle_terrain = slope <= SLOPE_THRESHOLD


print()
print("Thresholds")
print("Post-event VV <", LOW_VV_THRESHOLD, "dB")
print("Post-event VH <", LOW_VH_THRESHOLD, "dB")
print("VV change <", VV_CHANGE_THRESHOLD, "dB")
print("VH change <", VH_CHANGE_THRESHOLD, "dB")
print("Slope <=", SLOPE_THRESHOLD, "degrees")


print()
print("Pixels passing individual criteria")

print(
    "Low VV:",
    (valid & low_vv).sum(),
)

print(
    "Low VH:",
    (valid & low_vh).sum(),
)

print(
    "VV decrease:",
    (valid & vv_drop).sum(),
)

print(
    "VH decrease:",
    (valid & vh_drop).sum(),
)

print(
    "Slope constraint:",
    (valid & gentle_terrain).sum(),
)


candidate = (
    valid
    & low_vv
    & low_vh
    & vv_drop
    & vh_drop
    & gentle_terrain
)


print()
print("Initial candidate pixels:", candidate.sum())


candidate = binary_opening(
    candidate,
    structure=np.ones((3, 3), dtype=bool),
)

candidate = binary_closing(
    candidate,
    structure=np.ones((5, 5), dtype=bool),
)


labels, component_count = label(candidate)

print("Components before filtering:", component_count)


final_mask = np.zeros(
    candidate.shape,
    dtype=np.uint8,
)

component_sizes = []

for component_id in range(1, component_count + 1):

    component = labels == component_id
    size = int(component.sum())

    component_sizes.append(
        (component_id, size)
    )

    if size >= MINIMUM_PIXELS:
        final_mask[component] = 1


component_sizes.sort(
    key=lambda x: x[1],
    reverse=True,
)


print()
print("Component sizes")

for component_id, size in component_sizes:
    print(
        "Component",
        component_id,
        "| pixels:",
        size,
    )


print()
print("Components kept:", len(component_sizes))
print("Final candidate pixels:", int(final_mask.sum()))


candidate_percentage = (
    100.0
    * final_mask.sum()
    / valid.sum()
)

print(
    "Final candidate percentage:",
    candidate_percentage,
)


profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="lzw",
)


with rasterio.open(
    OUTPUT_MASK,
    "w",
    **profile,
) as dst:
    dst.write(final_mask, 1)


print()
print("Saved:", OUTPUT_MASK)