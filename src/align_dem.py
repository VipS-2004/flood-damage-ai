import os
import rasterio
import numpy as np

from rasterio.warp import reproject
from rasterio.enums import Resampling



# INPUTS


dem_file = "data/raw/copernicus_dem.tif"

reference_file = (
    "data/processed/"
    "sentinel1_20260816_VV_utm.tif"
)

output_file = (
    "data/processed/"
    "copernicus_dem_utm.tif"
)



# OUTPUT DIRECTORY


os.makedirs(
    "data/processed",
    exist_ok=True
)



# READ SENTINEL-1 REFERENCE GRID


with rasterio.open(reference_file) as ref:

    target_crs = ref.crs
    target_transform = ref.transform
    target_width = ref.width
    target_height = ref.height

    print("REFERENCE SENTINEL-1")
    print("--------------------")
    print("CRS:", target_crs)
    print("Size:", target_width, target_height)
    print("Resolution:", ref.res)
    print()



# READ DEM


with rasterio.open(dem_file) as src:

    print("ORIGINAL DEM")
    print("------------")
    print("CRS:", src.crs)
    print("Size:", src.width, src.height)
    print("Resolution:", src.res)
    print("NoData:", src.nodata)
    print("Bounds:", src.bounds)
    print()

    dem = src.read(1).astype(np.float32)

    source_crs = src.crs
    source_transform = src.transform
    source_nodata = src.nodata



# CREATE TARGET ARRAY


# Fill with NaN rather than arbitrary zero values.

dem_utm = np.full(
    (target_height, target_width),
    np.nan,
    dtype=np.float32
)



# REPROJECT DEM


reproject(
    source=dem,
    destination=dem_utm,

    src_transform=source_transform,
    src_crs=source_crs,

    dst_transform=target_transform,
    dst_crs=target_crs,

    src_nodata=source_nodata,
    dst_nodata=np.nan,

    resampling=Resampling.bilinear
)



# SAVE


profile = {
    "driver": "GTiff",
    "height": target_height,
    "width": target_width,
    "count": 1,
    "dtype": "float32",
    "crs": target_crs,
    "transform": target_transform,
    "nodata": np.nan,
    "compress": "lzw",
}


with rasterio.open(
    output_file,
    "w",
    **profile
) as dst:

    dst.write(
        dem_utm,
        1
    )



# VERIFY


with rasterio.open(output_file) as src:

    data = src.read(1)

    valid = np.isfinite(data)

    print()
    print("=" * 55)
    print("ALIGNED DEM")
    print("=" * 55)

    print("CRS:", src.crs)
    print("Size:", src.width, src.height)
    print("Resolution:", src.res)

    print(
        "Valid pixels:",
        np.sum(valid)
    )

    print(
        "Total pixels:",
        data.size
    )

    print(
        "Valid percentage:",
        np.mean(valid) * 100,
        "%"
    )

    if np.any(valid):

        print(
            "Elevation range:",
            np.min(data[valid]),
            "to",
            np.max(data[valid]),
            "m"
        )

    print("=" * 55)

print()
print("Saved:", output_file)