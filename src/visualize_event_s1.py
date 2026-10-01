import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap



# FILES


before_file = "data/raw/sentinel1_20260816_VV.tif"
after_file  = "data/raw/sentinel1_20260828_VV.tif"

output = "outputs/nepal_flood_sar_analysis.png"



# READ SENTINEL-1 DATA


with rasterio.open(before_file) as src:
    before = src.read(1).astype(np.float32)

with rasterio.open(after_file) as src:
    after = src.read(1).astype(np.float32)



# CHECK THAT IMAGES MATCH


if before.shape != after.shape:
    raise ValueError(
        f"Image dimensions do not match: "
        f"Before={before.shape}, After={after.shape}"
    )



# CONVERT TO dB


def to_db(data):

    data = data.copy()

    data[data <= 0] = np.nan

    return 10 * np.log10(data)


before_db = to_db(before)
after_db = to_db(after)



# VALID PIXELS


valid = (
    np.isfinite(before_db) &
    np.isfinite(after_db)
)



# VV CHANGE
#
# Positive = backscatter decreased after event
#
# Example:
# Before = -8 dB
# After  = -13 dB
#
# Change = -8 - (-13) = +5 dB
#
# Large positive values can indicate inundation.


change_db = np.full_like(before_db, np.nan)

change_db[valid] = (
    before_db[valid] - after_db[valid]
)



# FLOOD CANDIDATE THRESHOLD


threshold = 3.0   # dB

flood_mask = (
    valid &
    (change_db >= threshold)
)



# COMMON DISPLAY SCALE FOR BEFORE / AFTER


valid_before = before_db[np.isfinite(before_db)]
valid_after = after_db[np.isfinite(after_db)]

sar_values = np.concatenate([
    valid_before,
    valid_after
])

sar_vmin = np.percentile(sar_values, 2)
sar_vmax = np.percentile(sar_values, 98)



# CHANGE MAP SCALE


valid_change = change_db[np.isfinite(change_db)]

change_limit = np.percentile(
    np.abs(valid_change),
    98
)



# FIGURE


fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 10),
    constrained_layout=True
)



# 1. BEFORE


im1 = axes[0, 0].imshow(
    before_db,
    cmap="gray",
    vmin=sar_vmin,
    vmax=sar_vmax
)

axes[0, 0].set_title(
    "Before VV\n16 Aug 2026",
    fontsize=15,
    fontweight="bold"
)

axes[0, 0].set_xticks([])
axes[0, 0].set_yticks([])

cbar1 = fig.colorbar(
    im1,
    ax=axes[0, 0],
    fraction=0.046,
    pad=0.03
)

cbar1.set_label(
    "VV Backscatter (dB)",
    fontsize=10
)



# 2. AFTER


im2 = axes[0, 1].imshow(
    after_db,
    cmap="gray",
    vmin=sar_vmin,
    vmax=sar_vmax
)

axes[0, 1].set_title(
    "After VV\n28 Aug 2026",
    fontsize=15,
    fontweight="bold"
)

axes[0, 1].set_xticks([])
axes[0, 1].set_yticks([])

cbar2 = fig.colorbar(
    im2,
    ax=axes[0, 1],
    fraction=0.046,
    pad=0.03
)

cbar2.set_label(
    "VV Backscatter (dB)",
    fontsize=10
)



# 3. SAR CHANGE MAP


im3 = axes[1, 0].imshow(
    change_db,
    cmap="RdBu_r",
    vmin=-change_limit,
    vmax=change_limit
)

axes[1, 0].set_title(
    "VV Backscatter Change\nBefore − After",
    fontsize=15,
    fontweight="bold"
)

axes[1, 0].set_xticks([])
axes[1, 0].set_yticks([])

cbar3 = fig.colorbar(
    im3,
    ax=axes[1, 0],
    fraction=0.046,
    pad=0.03
)

cbar3.set_label(
    "Change (dB)",
    fontsize=10
)



# 4. FLOOD CANDIDATE MASK


# Create display image
mask_display = np.where(
    flood_mask,
    1,
    np.nan
)

im4 = axes[1, 1].imshow(
    mask_display,
    cmap="Blues",
    vmin=0,
    vmax=1
)

axes[1, 1].set_title(
    f"Flood Candidate Mask\nVV decrease ≥ {threshold:.1f} dB",
    fontsize=15,
    fontweight="bold"
)

axes[1, 1].set_xticks([])
axes[1, 1].set_yticks([])

cbar4 = fig.colorbar(
    im4,
    ax=axes[1, 1],
    fraction=0.046,
    pad=0.03
)

cbar4.set_ticks([0, 1])
cbar4.set_ticklabels([
    "No change",
    "Potential flood"
])



# MAIN TITLE


fig.suptitle(
    "Sentinel-1 SAR Flood Change Analysis | Nepal",
    fontsize=20,
    fontweight="bold"
)



# SAVE


plt.savefig(
    output,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved:", output)
print(f"Flood threshold: {threshold:.1f} dB")
print(
    "Potential flood pixels:",
    np.sum(flood_mask)
)