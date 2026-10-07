import rasterio
import numpy as np
import matplotlib.pyplot as plt

relief_path = "outputs/local_relief_31px.tif"

with rasterio.open(relief_path) as src:
    relief = src.read(1).astype(float)

relief[relief < 0] = np.nan
relief[relief >= 200] = np.nan

thresholds = [10, 20, 30, 50]

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

for ax, threshold in zip(axes.ravel(), thresholds):
    mask = relief <= threshold

    ax.imshow(mask, cmap="gray")
    ax.set_title(f"Local relief <= {threshold} m")
    ax.set_axis_off()

    percentage = np.sum(mask) / np.sum(np.isfinite(relief)) * 100

    ax.text(
        0.02,
        0.98,
        f"{percentage:.2f}% of valid area",
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.8)
    )

plt.tight_layout()

plt.savefig(
    "outputs/valley_thresholds.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("Saved: outputs/valley_thresholds.png")

valid = relief[np.isfinite(relief)]

for threshold in thresholds:
    percentage = np.mean(valid <= threshold) * 100
    print(f"Relief <= {threshold} m: {percentage:.2f}%")