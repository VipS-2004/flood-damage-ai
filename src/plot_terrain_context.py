import rasterio
import numpy as np
import matplotlib.pyplot as plt

dem_path = "outputs/dem_utm_aligned.tif"
slope_path = "outputs/dem_slope_utm.tif"

with rasterio.open(dem_path) as src:
    dem = src.read(1).astype(float)

with rasterio.open(slope_path) as src:
    slope = src.read(1).astype(float)

dem[dem <= -999] = np.nan
slope[slope < 0] = np.nan

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

im1 = axes[0].imshow(dem, cmap="terrain")
axes[0].set_title("Copernicus DEM")
axes[0].set_axis_off()
fig.colorbar(im1, ax=axes[0], label="Elevation")

im2 = axes[1].imshow(slope, cmap="viridis", vmin=0, vmax=60)
axes[1].set_title("Terrain Slope")
axes[1].set_axis_off()
fig.colorbar(im2, ax=axes[1], label="Slope (degrees)")

plt.tight_layout()

plt.savefig(
    "outputs/terrain_context.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("Saved: outputs/terrain_context.png")