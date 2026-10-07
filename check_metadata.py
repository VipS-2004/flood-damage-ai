import rasterio
import numpy as np

file = "data/raw/copernicus_dem.tif"

with rasterio.open(file) as src:

    print("CRS:", src.crs)
    print("Width:", src.width)
    print("Height:", src.height)
    print("Resolution:", src.res)
    print("Bounds:", src.bounds)

    print("NoData value:", src.nodata)

    data = src.read(1, masked=True)

    print()
    print("Valid pixels:", data.count())
    print("Total pixels:", data.size)

    if data.count() > 0:
        print("Minimum elevation:", data.min())
        print("Maximum elevation:", data.max())

    print(
        "Valid percentage:",
        data.count() / data.size * 100,
        "%"
    )