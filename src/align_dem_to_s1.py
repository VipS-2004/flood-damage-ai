import rasterio
from rasterio.warp import reproject, Resampling


REFERENCE = "data/raw/sentinel1_20260816_VV_utm.tif"
DEM_INPUT = "data/raw/copernicus_dem.tif"

DEM_OUTPUT = "outputs/dem_utm_aligned.tif"


with rasterio.open(REFERENCE) as ref:
    reference_profile = ref.profile.copy()
    reference_transform = ref.transform
    reference_crs = ref.crs
    reference_width = ref.width
    reference_height = ref.height

print("Reference Sentinel-1")
print("CRS:", reference_crs)
print("Size:", reference_width, "x", reference_height)
print("Pixel size:", reference_transform.a, abs(reference_transform.e))


with rasterio.open(DEM_INPUT) as src:

    dem = src.read(1)

    aligned_dem = dem.astype("float32")

    profile = reference_profile.copy()

    profile.update(
        dtype="float32",
        count=1,
        nodata=-9999,
        compress="lzw",
    )

    reproject(
        source=dem,
        destination=aligned_dem,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=reference_transform,
        dst_crs=reference_crs,
        dst_shape=(reference_height, reference_width),
        resampling=Resampling.bilinear,
    )


with rasterio.open(DEM_OUTPUT, "w", **profile) as dst:
    dst.write(aligned_dem, 1)


print()
print("Saved:", DEM_OUTPUT)
print("CRS:", reference_crs)
print("Size:", reference_width, "x", reference_height)