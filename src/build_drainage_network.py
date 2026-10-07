import numpy as np
import rasterio
from pathlib import Path
from pysheds.grid import Grid

if not hasattr(np, "in1d"):
    np.in1d = np.isin

DEM = Path("outputs/dem_utm_aligned.tif")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

grid = Grid.from_raster(str(DEM))

dem = grid.read_raster(str(DEM))

print("DEM loaded")
print("Shape:", dem.shape)
print("Minimum elevation:", float(np.nanmin(dem)))
print("Maximum elevation:", float(np.nanmax(dem)))

pit_filled = grid.fill_pits(dem)
depressions_filled = grid.fill_depressions(pit_filled)
inflated = grid.resolve_flats(depressions_filled)

fdir = grid.flowdir(inflated)
acc = grid.accumulation(fdir)

acc_array = np.asarray(acc)

print("Flow accumulation calculated")
print("Maximum accumulation:", float(np.nanmax(acc_array)))

with rasterio.open(DEM) as src:
    profile = src.profile.copy()

profile.update(
    dtype="float32",
    count=1,
    nodata=-9999
)

with rasterio.open(
    OUTPUT_DIR / "flow_accumulation.tif",
    "w",
    **profile
) as dst:
    output = np.asarray(acc_array, dtype=np.float32)
    output[~np.isfinite(output)] = -9999
    dst.write(output, 1)

print("Saved:", OUTPUT_DIR / "flow_accumulation.tif")