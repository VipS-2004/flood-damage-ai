import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling



# INPUT / OUTPUT


files = {
    "before_vv": "data/raw/sentinel1_20260816_VV.tif",
    "after_vv": "data/raw/sentinel1_20260828_VV.tif",

    "before_vh": "data/raw/sentinel1_20260816_VH.tif",
    "after_vh": "data/raw/sentinel1_20260828_VH.tif",
}

outputs = {
    "before_vv": "data/processed/sentinel1_20260816_VV_utm.tif",
    "after_vv": "data/processed/sentinel1_20260828_VV_utm.tif",

    "before_vh": "data/processed/sentinel1_20260816_VH_utm.tif",
    "after_vh": "data/processed/sentinel1_20260828_VH_utm.tif",
}



# TARGET CRS


target_crs = "EPSG:32645"



# REPROJECT FUNCTION


def reproject_raster(input_file, output_file):

    with rasterio.open(input_file) as src:

        transform, width, height = calculate_default_transform(
            src.crs,
            target_crs,
            src.width,
            src.height,
            *src.bounds
        )

        profile = src.profile.copy()

        profile.update({
            "crs": target_crs,
            "transform": transform,
            "width": width,
            "height": height,
            "compress": "lzw"
        })

        with rasterio.open(output_file, "w", **profile) as dst:

            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),

                src_transform=src.transform,
                src_crs=src.crs,

                dst_transform=transform,
                dst_crs=target_crs,

                resampling=Resampling.bilinear
            )

    print(f"Saved: {output_file}")



# CREATE OUTPUT DIRECTORY


import os

os.makedirs(
    "data/processed",
    exist_ok=True
)



# REPROJECT BOTH IMAGES


for name in files:

    reproject_raster(
        files[name],
        outputs[name]
    )



# VERIFY OUTPUT


print()
print("=" * 50)
print("VERIFYING REPROJECTED FILES")
print("=" * 50)

for name, filepath in outputs.items():

    with rasterio.open(filepath) as src:

        print()
        print(name.upper())
        print("CRS:", src.crs)
        print("Resolution:", src.res)
        print("Width:", src.width)
        print("Height:", src.height)
        print("Bounds:", src.bounds)