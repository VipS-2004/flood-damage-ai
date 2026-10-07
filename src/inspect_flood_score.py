import rasterio
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label


INPUT = "outputs/event_flood_score.tif"


with rasterio.open(INPUT) as src:

    score = src.read(1)

    profile = src.profile.copy()


valid = np.isfinite(score)

values = score[valid]


thresholds = {
    "90th percentile": np.percentile(values, 90),
    "95th percentile": np.percentile(values, 95),
    "99th percentile": np.percentile(values, 99)
}


print("Thresholds:")

for name, threshold in thresholds.items():

    mask = (
        valid &
        (score >= threshold)
    )

    print(
        name,
        "=",
        threshold,
        "| pixels:",
        mask.sum(),
        "| percentage:",
        mask.sum() / valid.sum() * 100
    )


fig, axes = plt.subplots(
    1,
    3,
    figsize=(15, 6)
)


for ax, (name, threshold) in zip(
    axes,
    thresholds.items()
):

    mask = (
        valid &
        (score >= threshold)
    )

    ax.imshow(
        mask,
        cmap="gray"
    )

    ax.set_title(
        f"{name}\nScore >= {threshold:.3f}",
        fontsize=13,
        pad=12
    )

    ax.set_xticks([])
    ax.set_yticks([])


fig.suptitle(
    "Flood Score Threshold Comparison",
    fontsize=17,
    y=0.98
)


plt.subplots_adjust(
    left=0.03,
    right=0.97,
    bottom=0.05,
    top=0.85,
    wspace=0.12
)


output = (
    "outputs/event_flood_score_thresholds.png"
)


plt.savefig(
    output,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved:", output)