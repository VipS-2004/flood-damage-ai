import rasterio
import numpy as np


INPUT = "data/raw/copernicus_dem.tif"
OUTPUT = "outputs/dem_slope.tif"


with rasterio.open(INPUT) as src:

    dem = src.read(1).astype(np.float32)

    profile = src.profile

    transform = src.transform


# Pixel size in degrees
pixel_x = abs(transform.a)
pixel_y = abs(transform.e)

# Approximate meters per degree at this latitude
lat = 28.0

meters_per_degree_lat = 111320
meters_per_degree_lon = 111320 * np.cos(np.radians(lat))

dx = pixel_x * meters_per_degree_lon
dy = pixel_y * meters_per_degree_lat


# Calculate elevation gradients
gradient_y, gradient_x = np.gradient(
    dem,
    dy,
    dx
)


# Slope in degrees
slope = np.degrees(
    np.arctan(
        np.sqrt(
            gradient_x ** 2 +
            gradient_y ** 2
        )
    )
)


profile.update(
    dtype="float32",
    count=1,
    compress="lzw"
)


with rasterio.open(OUTPUT, "w", **profile) as dst:

    dst.write(
        slope.astype(np.float32),
        1
    )


print("DEM processed successfully")
print("Slope min:", np.nanmin(slope))
print("Slope max:", np.nanmax(slope))
print("Slope mean:", np.nanmean(slope))
print("Saved:", OUTPUT)