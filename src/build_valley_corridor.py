import rasterio
import numpy as np
from scipy.ndimage import binary_dilation
import matplotlib.pyplot as plt

relief_path = "outputs/local_relief_31px.tif"

with rasterio.open(relief_path) as src:
    relief = src.read(1).astype(float)
    profile = src.profile

relief[relief < 0] = np.nan
relief[relief >= 200] = np.nan

valid = np.isfinite(relief)

valley_core = valid & (relief <= 30)

pixel_size = profile["transform"].a
buffer_m = 130
iterations = round(buffer_m / pixel_size)

valley_corridor = binary_dilation(
    valley_core,
    iterations=iterations
)

valley_corridor &= valid

profile.update(
    dtype="uint8",
    count=1,
    nodata=0
)

with rasterio.open(
    "outputs/valley_corridor.tif",
    "w",
    **profile
) as dst:
    dst.write(valley_corridor.astype("uint8"), 1)

plt.figure(figsize=(8, 6))

plt.imshow(valley_corridor, cmap="gray")

plt.title("Terrain-Derived Valley Corridor")
plt.axis("off")

plt.tight_layout()

plt.savefig(
    "outputs/valley_corridor.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

percentage = (
    np.sum(valley_corridor) /
    np.sum(valid) *
    100
)

print(f"Pixel size: {pixel_size:.2f} m")
print(f"Dilation distance: {iterations * pixel_size:.2f} m")
print(f"Corridor area: {percentage:.2f}%")
print("Saved: outputs/valley_corridor.tif")
print("Saved: outputs/valley_corridor.png")