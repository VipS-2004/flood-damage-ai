import rasterio
import numpy as np
from scipy.ndimage import minimum_filter
import matplotlib.pyplot as plt

dem_path = "outputs/dem_utm_aligned.tif"

with rasterio.open(dem_path) as src:
    dem = src.read(1).astype(float)

    profile = src.profile

dem[dem <= -999] = np.nan

window = 31

valid = np.isfinite(dem)

filled_dem = np.where(valid, dem, np.nanmedian(dem))

local_min = minimum_filter(
    filled_dem,
    size=window,
    mode="nearest"
)

local_relief = dem - local_min
local_relief[~valid] = np.nan

profile.update(
    dtype="float32",
    count=1,
    nodata=-9999
)

output = np.where(
    np.isfinite(local_relief),
    local_relief,
    -9999
).astype("float32")

with rasterio.open(
    "outputs/local_relief_31px.tif",
    "w",
    **profile
) as dst:
    dst.write(output, 1)

fig, ax = plt.subplots(figsize=(8, 6))

image = ax.imshow(
    local_relief,
    cmap="viridis",
    vmin=0,
    vmax=200
)

ax.set_title("Local Relief from DEM")
ax.set_axis_off()

fig.colorbar(
    image,
    ax=ax,
    label="Elevation above local minimum (m)"
)

plt.tight_layout()

plt.savefig(
    "outputs/local_relief_31px.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("Saved: outputs/local_relief_31px.tif")
print("Saved: outputs/local_relief_31px.png")

values = local_relief[np.isfinite(local_relief)]

print(f"Relief median: {np.median(values):.2f} m")
print(f"Relief p25: {np.percentile(values, 25):.2f} m")
print(f"Relief p50: {np.percentile(values, 50):.2f} m")
print(f"Relief p75: {np.percentile(values, 75):.2f} m")
print(f"Relief p90: {np.percentile(values, 90):.2f} m")