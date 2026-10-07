import rasterio
import numpy as np


DEM = "outputs/dem_utm_aligned.tif"
OUTPUT = "outputs/dem_slope_utm.tif"


with rasterio.open(DEM) as src:
    dem = src.read(1).astype(np.float32)
    profile = src.profile.copy()

    pixel_x = abs(src.transform.a)
    pixel_y = abs(src.transform.e)

    nodata = src.nodata

print("DEM CRS:", profile["crs"])
print("DEM shape:", dem.shape)
print("Pixel size:", pixel_x, pixel_y)
print("DEM min:", np.nanmin(dem))
print("DEM max:", np.nanmax(dem))

if nodata is not None:
    valid = dem != nodata
else:
    valid = np.isfinite(dem)

dem_clean = dem.copy()

if nodata is not None:
    dem_clean[~valid] = np.nan

gradient_y, gradient_x = np.gradient(
    dem_clean,
    pixel_y,
    pixel_x,
)

slope = np.degrees(
    np.arctan(
        np.sqrt(
            gradient_x ** 2
            + gradient_y ** 2
        )
    )
)

slope[~valid] = np.nan

print()
print("Slope statistics")
print("Min:", np.nanmin(slope))
print("Median:", np.nanmedian(slope))
print("Mean:", np.nanmean(slope))
print("Max:", np.nanmax(slope))

profile.update(
    dtype="float32",
    count=1,
    nodata=-9999,
    compress="lzw",
)

output_slope = np.where(
    np.isfinite(slope),
    slope,
    -9999,
).astype(np.float32)

with rasterio.open(OUTPUT, "w", **profile) as dst:
    dst.write(output_slope, 1)

print()
print("Saved:", OUTPUT)