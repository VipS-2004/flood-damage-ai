import rasterio
import matplotlib.pyplot as plt

DRAINAGE = "outputs/main_drainage_10000.tif"
CORRIDOR = "outputs/drainage_corridor_100m.tif"
OUTPUT = "outputs/drainage_corridor_100m.png"

with rasterio.open(DRAINAGE) as src:
    drainage = src.read(1)
    bounds = src.bounds

with rasterio.open(CORRIDOR) as src:
    corridor = src.read(1)

extent = [
    bounds.left,
    bounds.right,
    bounds.bottom,
    bounds.top
]

fig, ax = plt.subplots(figsize=(12, 10))

ax.imshow(
    corridor,
    extent=extent,
    origin="upper",
    alpha=0.35
)

ax.imshow(
    drainage,
    extent=extent,
    origin="upper",
    alpha=0.8
)

ax.set_title("Hydrologic Drainage Network and 100 m Corridor")
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")

plt.tight_layout()
plt.savefig(OUTPUT, dpi=200, bbox_inches="tight")
plt.close()

print(f"Saved: {OUTPUT}")