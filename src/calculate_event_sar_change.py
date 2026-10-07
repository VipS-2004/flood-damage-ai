import rasterio
import numpy as np
import matplotlib.pyplot as plt


before_files = {
    "VV": "data/raw/sentinel1_20260816_VV.tif",
    "VH": "data/raw/sentinel1_20260816_VH.tif"
}

after_files = {
    "VV": "data/raw/sentinel1_20260828_VV.tif",
    "VH": "data/raw/sentinel1_20260828_VH.tif"
}


def to_db(data):

    data = data.astype(np.float32)

    data[data <= 0] = np.nan

    return 10 * np.log10(data)


changes = {}


for band in ["VV", "VH"]:

    with rasterio.open(before_files[band]) as src:

        before = src.read(1)
        profile = src.profile.copy()

    with rasterio.open(after_files[band]) as src:

        after = src.read(1)

    before_db = to_db(before)
    after_db = to_db(after)

    change = after_db - before_db

    changes[band] = change

    # Save GeoTIFF
    profile.update(
        dtype="float32",
        count=1,
        nodata=np.nan,
        compress="lzw"
    )

    output_tif = (
        f"outputs/event_{band.lower()}_change.tif"
    )

    with rasterio.open(
        output_tif,
        "w",
        **profile
    ) as dst:

        dst.write(
            change.astype(np.float32),
            1
        )

    print()
    print(f"{band} change")

    valid = change[np.isfinite(change)]

    print("Minimum:", np.percentile(valid, 1))
    print("Median:", np.percentile(valid, 50))
    print("Maximum:", np.percentile(valid, 99))

    print("Saved:", output_tif)


# ------------------------------------------------
# Visualization
# ------------------------------------------------

fig, axes = plt.subplots(
    1,
    2,
    figsize=(13, 6)
)


for ax, band in zip(
    axes,
    ["VV", "VH"]
):

    change = changes[band]

    valid = change[np.isfinite(change)]

    # Symmetric range around zero
    limit = np.percentile(
        np.abs(valid),
        98
    )

    im = ax.imshow(
        change,
        cmap="RdBu_r",
        vmin=-limit,
        vmax=limit
    )

    ax.set_title(
        f"{band} SAR Change\n28 Aug - 16 Aug 2026",
        fontsize=13,
        pad=12
    )

    ax.set_xticks([])
    ax.set_yticks([])

    cbar = fig.colorbar(
        im,
        ax=ax,
        fraction=0.046,
        pad=0.03
    )

    cbar.set_label(
        "Change (dB)",
        fontsize=10
    )


fig.suptitle(
    "Sentinel-1 SAR Change Detection",
    fontsize=17,
    y=0.97
)


plt.subplots_adjust(
    left=0.05,
    right=0.94,
    bottom=0.06,
    top=0.87,
    wspace=0.22
)


output_png = (
    "outputs/event_sar_change.png"
)

plt.savefig(
    output_png,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved:", output_png)