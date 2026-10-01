import rasterio
import matplotlib.pyplot as plt


INPUT = "outputs/dem_slope.tif"
OUTPUT = "outputs/dem_slope.png"


with rasterio.open(INPUT) as src:
    slope = src.read(1)


plt.figure(figsize=(8, 7))

plt.imshow(
    slope,
    cmap="terrain",
    vmin=0,
    vmax=60
)

plt.colorbar(
    label="Slope (degrees)"
)

plt.title("Terrain Slope")

plt.axis("off")

plt.tight_layout()

plt.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print("Saved:", OUTPUT)