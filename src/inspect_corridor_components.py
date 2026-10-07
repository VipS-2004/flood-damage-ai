import numpy as np
import rasterio
from scipy.ndimage import label

INPUT = "outputs/valley_corridor.tif"

with rasterio.open(INPUT) as src:
    corridor = src.read(1)
    pixel_area = abs(src.transform.a * src.transform.e)

mask = corridor == 1

labels, count = label(mask)

sizes = np.bincount(labels.ravel())
sizes = sizes[1:]

sizes_sorted = np.sort(sizes)[::-1]

print(f"Connected components: {count}")
print(f"Pixel area: {pixel_area:.2f} m²")

print("\nLargest components:")
for i, size in enumerate(sizes_sorted[:20], start=1):
    area_ha = size * pixel_area / 10000
    print(f"{i:2d}. {size:8d} pixels | {area_ha:8.2f} ha")