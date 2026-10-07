import rasterio
from rasterio.warp import reproject, Resampling
from pathlib import Path

REFERENCE = Path("data/raw/sentinel1_20260816_VV_utm.tif")
INPUT_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files = [
    "sentinel1_20260816_VV_gamma0terrain.tif",
    "sentinel1_20260816_VH_gamma0terrain.tif",
    "sentinel1_20260828_VV_gamma0terrain.tif",
    "sentinel1_20260828_VH_gamma0terrain.tif",
]

with rasterio.open(REFERENCE) as ref:
    ref_crs = ref.crs
    ref_transform = ref.transform
    ref_width = ref.width
    ref_height = ref.height

for filename in files:
    input_file = INPUT_DIR / filename
    output_file = OUTPUT_DIR / filename.replace(".tif", "_utm_aligned.tif")

    with rasterio.open(input_file) as src:
        profile = src.profile.copy()

        profile.update(
            crs=ref_crs,
            transform=ref_transform,
            width=ref_width,
            height=ref_height,
            dtype="float32",
            count=1
        )

        with rasterio.open(output_file, "w", **profile) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=ref_transform,
                dst_crs=ref_crs,
                resampling=Resampling.bilinear
            )

    print(f"Saved: {output_file}")