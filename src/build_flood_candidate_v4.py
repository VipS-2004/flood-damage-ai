import rasterio
import numpy as np
from scipy.ndimage import binary_opening, binary_closing, label


VV_BEFORE = "data/raw/sentinel1_20260816_VV_utm.tif"
VH_BEFORE = "data/raw/sentinel1_20260816_VH_utm.tif"

VV_AFTER = "data/raw/sentinel1_20260828_VV_utm.tif"
VH_AFTER = "data/raw/sentinel1_20260828_VH_utm.tif"

SLOPE = "outputs/dem_slope_utm.tif"

OUTPUT = "outputs/event_flood_candidate_v4.tif"


def read_raster(path):
    with rasterio.open(path) as src:
        data = src.read(1).astype(np.float32)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs

    return data, profile, transform, crs


def to_db(data):
    data = data.copy()
    data[data <= 0] = np.nan
    return 10.0 * np.log10(data)


vv_before_raw, profile, transform, crs = read_raster(VV_BEFORE)
vh_before_raw, _, _, _ = read_raster(VH_BEFORE)
vv_after_raw, _, _, _ = read_raster(VV_AFTER)
vh_after_raw, _, _, _ = read_raster(VH_AFTER)
slope, _, _, _ = read_raster(SLOPE)


print("Reference grid")
print("Shape:", vv_before_raw.shape)
print("CRS:", crs)
print("Pixel size:", abs(transform.a), abs(transform.e))


if not (
    vv_before_raw.shape
    == vh_before_raw.shape
    == vv_after_raw.shape
    == vh_after_raw.shape
    == slope.shape
):
    raise ValueError("Input rasters do not have identical dimensions.")


vv_before = to_db(vv_before_raw)
vh_before = to_db(vh_before_raw)

vv_after = to_db(vv_after_raw)
vh_after = to_db(vh_after_raw)


vv_change = vv_after - vv_before
vh_change = vh_after - vh_before


valid = (
    np.isfinite(vv_before)
    & np.isfinite(vh_before)
    & np.isfinite(vv_after)
    & np.isfinite(vh_after)
    & np.isfinite(vv_change)
    & np.isfinite(vh_change)
    & np.isfinite(slope)
    & (slope >= 0)
)


print()
print("Valid pixels:", valid.sum())


print()
print("Post-event statistics")

print(
    "VV p1/p5/p10/median:",
    np.nanpercentile(vv_after, 1),
    np.nanpercentile(vv_after, 5),
    np.nanpercentile(vv_after, 10),
    np.nanmedian(vv_after),
)

print(
    "VH p1/p5/p10/median:",
    np.nanpercentile(vh_after, 1),
    np.nanpercentile(vh_after, 5),
    np.nanpercentile(vh_after, 10),
    np.nanmedian(vh_after),
)


print()
print("Change statistics")

print(
    "VV change p1/p5/median:",
    np.nanpercentile(vv_change, 1),
    np.nanpercentile(vv_change, 5),
    np.nanmedian(vv_change),
)

print(
    "VH change p1/p5/median:",
    np.nanpercentile(vh_change, 1),
    np.nanpercentile(vh_change, 5),
    np.nanmedian(vh_change),
)


print()
print("Slope statistics")

print(
    "p10:",
    np.nanpercentile(slope[valid], 10),
)

print(
    "median:",
    np.nanmedian(slope[valid]),
)

print(
    "p25:",
    np.nanpercentile(slope[valid], 25),
)

print(
    "p50:",
    np.nanpercentile(slope[valid], 50),
)

print(
    "p75:",
    np.nanpercentile(slope[valid], 75),
)


LOW_VV = -15.0
LOW_VH = -20.0

VV_DROP = -1.0
VH_DROP = -1.0

MAX_SLOPE = 30.0


low_vv = vv_after < LOW_VV
low_vh = vh_after < LOW_VH

vv_drop = vv_change < VV_DROP
vh_drop = vh_change < VH_DROP

gentle = slope <= MAX_SLOPE


print()
print("Criteria")

print("VV <", LOW_VV, "dB")
print("VH <", LOW_VH, "dB")
print("VV change <", VV_DROP, "dB")
print("VH change <", VH_DROP, "dB")
print("Slope <=", MAX_SLOPE, "degrees")


print()
print("Individual criterion counts")

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
    (valid & gentle).sum(),
)


candidate = (
    valid
    & low_vv
    & low_vh
    & vv_drop
    & vh_drop
    & gentle
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


labels, count = label(candidate)


MIN_PIXELS = 10

final_mask = np.zeros(
    candidate.shape,
    dtype=np.uint8,
)


components = []


for component_id in range(1, count + 1):

    component = labels == component_id
    size = int(component.sum())

    components.append(
        (component_id, size)
    )

    if size >= MIN_PIXELS:
        final_mask[component] = 1


components.sort(
    key=lambda x: x[1],
    reverse=True,
)


print()
print("Connected components:", count)

print("Component sizes:")

for component_id, size in components[:20]:
    print(
        "Component",
        component_id,
        "|",
        size,
        "pixels",
    )


print()
print("Final candidate pixels:", int(final_mask.sum()))

candidate_percentage = (
    100.0
    * final_mask.sum()
    / valid.sum()
)

print(
    "Candidate percentage:",
    candidate_percentage,
)


pixel_area = abs(transform.a * transform.e)

area_m2 = final_mask.sum() * pixel_area
area_ha = area_m2 / 10000.0
area_km2 = area_m2 / 1_000_000.0


print("Pixel area:", pixel_area, "m²")
print("Candidate area:", area_m2, "m²")
print("Candidate area:", area_ha, "ha")
print("Candidate area:", area_km2, "km²")


profile.update(
    dtype="uint8",
    count=1,
    nodata=0,
    compress="lzw",
)


with rasterio.open(
    OUTPUT,
    "w",
    **profile,
) as dst:
    dst.write(final_mask, 1)


print()
print("Saved:", OUTPUT)