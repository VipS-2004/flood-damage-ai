import rasterio
import numpy as np
import matplotlib.pyplot as plt



# INPUT


dem_file = (
    "data/processed/"
    "copernicus_dem_utm.tif"
)



# READ DEM


with rasterio.open(dem_file) as src:

    dem = src.read(
        1,
        masked=True
    ).astype(np.float32)

    pixel_x = abs(src.transform.a)
    pixel_y = abs(src.transform.e)

    crs = src.crs

    # Convert masked values to NaN
    dem = dem.filled(np.nan)



# INVALID VALUES


dem[~np.isfinite(dem)] = np.nan



# CALCULATE ELEVATION GRADIENT


gradient_y, gradient_x = np.gradient(
    dem,
    pixel_y,
    pixel_x
)



# SLOPE


slope_radians = np.arctan(
    np.sqrt(
        gradient_x ** 2 +
        gradient_y ** 2
    )
)

slope_degrees = np.degrees(
    slope_radians
)



# STATISTICS


valid_slope = slope_degrees[
    np.isfinite(slope_degrees)
]


print()
print("=" * 55)
print("TERRAIN / SLOPE ANALYSIS")
print("=" * 55)

print("CRS:", crs)

print(
    f"Pixel size: "
    f"{pixel_x:.3f} × "
    f"{pixel_y:.3f} m"
)

print(
    f"Minimum slope: "
    f"{np.min(valid_slope):.2f}°"
)

print(
    f"Maximum slope: "
    f"{np.max(valid_slope):.2f}°"
)

print(
    f"Mean slope: "
    f"{np.mean(valid_slope):.2f}°"
)

print(
    f"Median slope: "
    f"{np.median(valid_slope):.2f}°"
)

print()

for threshold in [5, 10, 15, 20, 30]:

    percentage = (
        np.mean(
            valid_slope <= threshold
        ) * 100
    )

    print(
        f"Area with slope ≤ "
        f"{threshold:2d}°: "
        f"{percentage:.2f}%"
    )

print("=" * 55)



# VISUALIZE SLOPE


plt.figure(
    figsize=(10, 7)
)

image = plt.imshow(
    slope_degrees,
    cmap="terrain",
    vmin=0,
    vmax=np.percentile(
        valid_slope,
        98
    )
)

plt.colorbar(
    image,
    label="Slope (degrees)"
)

plt.title(
    "Terrain Slope | Nepal Study Area",
    fontsize=17,
    fontweight="bold"
)

plt.xticks([])
plt.yticks([])

plt.tight_layout()

output = (
    "outputs/nepal_slope_map.png"
)

plt.savefig(
    output,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved:", output)