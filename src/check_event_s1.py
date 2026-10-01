import rasterio
import numpy as np


files = [
    "data/raw/sentinel1_20260816_VV.tif",
    "data/raw/sentinel1_20260816_VH.tif",
    "data/raw/sentinel1_20260828_VV.tif",
    "data/raw/sentinel1_20260828_VH.tif",
]


for filepath in files:

    print("=" * 60)
    print(filepath)

    with rasterio.open(filepath) as src:

        data = src.read(1)

        valid = np.isfinite(data)

        print("Size:", src.width, "x", src.height)
        print("CRS:", src.crs)
        print("Bounds:", src.bounds)

        print(
            "Valid pixels:",
            valid.sum(),
            "/",
            data.size
        )

        print(
            "Min:",
            np.nanmin(data)
        )

        print(
            "Max:",
            np.nanmax(data)
        )

        print(
            "Mean:",
            np.nanmean(data)
        )

        print()