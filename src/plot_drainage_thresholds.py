import numpy as np
import rasterio
import matplotlib.pyplot as plt

INPUT = "outputs/flow_accumulation.tif"
OUTPUT = "outputs/drainage_thresholds.png"

thresholds = [1000, 5000, 10000, 50000]

with rasterio.open(INPUT) as src:
    acc = src.read(1)
    nodata = src.nodata
    bounds = src.bounds

acc = acc.astype(float)
acc[acc == nodata] = np.nan

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for ax, threshold in zip(axes.ravel(), thresholds):
    drainage = acc >= threshold

    ax.imshow(
        drainage,
        extent=[
            bounds.left,
            bounds.right,
            bounds.bottom,
            bounds.top
        ],
        origin="upper"
    )

    ax.set_title(
        f"Flow accumulation >= {threshold:,} cells"
    )

    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")

plt.tight_layout()
plt.savefig(OUTPUT, dpi=200)
plt.close()

print(f"Saved: {OUTPUT}")