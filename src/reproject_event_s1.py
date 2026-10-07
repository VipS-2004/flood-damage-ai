import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling


INPUTS = [
    "data/raw/sentinel1_20260816_VV.tif",
    "data/raw/sentinel1_20260816_VH.tif",
    "data/raw/sentinel1_20260828_VV.tif",
    "data/raw/sentinel1_20260828_VH.tif",
]

OUTPUTS = [
    "data/raw/sentinel1_20260816_VV_utm.tif",
    "data/raw/sentinel1_20260816_VH_utm.tif",
    "data/raw/sentinel1_20260828_VV_utm.tif",
    "data/raw/sentinel1_20260828_VH_utm.tif",
]

TARGET_CRS = "EPSG:32645"


for input_path, output_path in zip(INPUTS, OUTPUTS):

    print()
    print("Processing:", input_path)

    with rasterio.open(input_path) as src:

        transform, width, height = calculate_default_transform(
            src.crs,
            TARGET_CRS,
            src.width,
            src.height,
            *src.bounds,
        )

        profile = src.profile.copy()

        profile.update(
            crs=TARGET_CRS,
            transform=transform,
            width=width,
            height=height,
            compress="lzw",
        )

        with rasterio.open(output_path, "w", **profile) as dst:

            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=TARGET_CRS,
                resampling=Resampling.bilinear,
            )

    print("Saved:", output_path)
    print("Size:", width, "x", height)