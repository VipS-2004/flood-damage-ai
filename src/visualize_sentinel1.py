import rasterio
import numpy as np
import matplotlib.pyplot as plt


FILES = {
    "Before VV": "data/raw/sentinel1_20260819_VV.tif",
    "After VV": "data/raw/sentinel1_20260831_VV.tif",
    "Before VH": "data/raw/sentinel1_20260819_VH.tif",
    "After VH": "data/raw/sentinel1_20260831_VH.tif",
}


def read_raster(path):
    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32)


def to_db(image):
    """
    Convert Sentinel-1 linear backscatter to dB.
    Zero/invalid pixels become NaN.
    """
    image = image.astype(np.float32)

    result = np.full_like(image, np.nan)

    valid = image > 0

    result[valid] = 10 * np.log10(image[valid])

    return result


def percentile_limits(image, low=2, high=98):
    valid = image[np.isfinite(image)]

    return np.percentile(valid, [low, high])



# Read data


images = {}

for name, path in FILES.items():

    linear = read_raster(path)

    images[name] = to_db(linear)

    valid = images[name][np.isfinite(images[name])]

    print(
        name,
        "| valid pixels:", len(valid),
        "| min:", np.min(valid),
        "| max:", np.max(valid),
        "| mean:", np.mean(valid)
    )



# Radar change


vv_change = (
    images["After VV"] -
    images["Before VV"]
)

vh_change = (
    images["After VH"] -
    images["Before VH"]
)



# Change statistics


vv_valid = vv_change[np.isfinite(vv_change)]
vh_valid = vh_change[np.isfinite(vh_change)]

print("\nVV change:")
print("min:", np.min(vv_valid))
print("max:", np.max(vv_valid))
print("mean:", np.mean(vv_valid))

print("\nVH change:")
print("min:", np.min(vh_valid))
print("max:", np.max(vh_valid))
print("mean:", np.mean(vh_valid))



# Visualization limits


vv_min, vv_max = percentile_limits(images["Before VV"])
vh_min, vh_max = percentile_limits(images["Before VH"])

vv_change_min, vv_change_max = percentile_limits(
    vv_change
)

vh_change_min, vh_change_max = percentile_limits(
    vh_change
)

# Use symmetric limits for change maps
vv_limit = max(
    abs(vv_change_min),
    abs(vv_change_max)
)

vh_limit = max(
    abs(vh_change_min),
    abs(vh_change_max)
)



# Plot


fig, axes = plt.subplots(
    2,
    3,
    figsize=(15, 9)
)


# VV

axes[0, 0].imshow(
    images["Before VV"],
    cmap="gray",
    vmin=vv_min,
    vmax=vv_max
)

axes[0, 0].set_title(
    "Before VV (dB)"
)


axes[0, 1].imshow(
    images["After VV"],
    cmap="gray",
    vmin=vv_min,
    vmax=vv_max
)

axes[0, 1].set_title(
    "After VV (dB)"
)


axes[0, 2].imshow(
    vv_change,
    cmap="RdBu_r",
    vmin=-vv_limit,
    vmax=vv_limit
)

axes[0, 2].set_title(
    "VV Change (dB)"
)


# VH

axes[1, 0].imshow(
    images["Before VH"],
    cmap="gray",
    vmin=vh_min,
    vmax=vh_max
)

axes[1, 0].set_title(
    "Before VH (dB)"
)


axes[1, 1].imshow(
    images["After VH"],
    cmap="gray",
    vmin=vh_min,
    vmax=vh_max
)

axes[1, 1].set_title(
    "After VH (dB)"
)


axes[1, 2].imshow(
    vh_change,
    cmap="RdBu_r",
    vmin=-vh_limit,
    vmax=vh_limit
)

axes[1, 2].set_title(
    "VH Change (dB)"
)


for ax in axes.flat:
    ax.axis("off")


plt.tight_layout()


# Save only. No GUI window.
output = "outputs/sentinel1_change_db.png"

plt.savefig(
    output,
    dpi=200,
    bbox_inches="tight"
)

plt.close()

print("\nSaved:", output)