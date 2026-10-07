import numpy as np
import rasterio
from pathlib import Path

INPUT = Path("outputs/flow_accumulation.tif")
OUTPUT = Path("outputs/main_drainage_10000.tif")

THRESHOLD = 10000

with rasterio.open(INPUT) as src:
    acc = src.read(1)
    profile = src.profile.copy()
    nodata = src.nodata

drainage = np.zeros(acc.shape, dtype=np.uint8)

valid = np.isfinite(acc)

if nodata is not None:
    valid &= acc != nodata

drainage[valid & (acc >= THRESHOLD)] = 1

profile.update(
    dtype="uint8",
    count=1,
    nodata=0
)

with rasterio.open(OUTPUT, "w", **profile) as dst:
    dst.write(drainage, 1)

print(f"Threshold: {THRESHOLD:,} cells")
print(f"Drainage cells: {np.sum(drainage == 1):,}")
print(f"Saved: {OUTPUT}")