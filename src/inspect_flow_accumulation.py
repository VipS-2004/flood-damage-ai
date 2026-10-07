import numpy as np
import rasterio

INPUT = "outputs/flow_accumulation.tif"

with rasterio.open(INPUT) as src:
    acc = src.read(1)
    nodata = src.nodata

valid = acc != nodata
values = acc[valid]
values = values[np.isfinite(values)]
values = values[values > 0]

percentiles = [50, 75, 90, 95, 97, 98, 99, 99.5, 99.9]

print("Flow accumulation statistics")
print(f"Valid cells: {len(values):,}")
print(f"Minimum: {values.min():,.0f}")
print(f"Median: {np.percentile(values, 50):,.0f}")
print(f"Maximum: {values.max():,.0f}")

print("\nPercentiles:")
for p in percentiles:
    print(f"P{p}: {np.percentile(values, p):,.0f}")

print("\nCell counts above thresholds:")
for threshold in [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]:
    count = np.sum(values >= threshold)
    print(f">= {threshold:>6,}: {count:>8,} cells")