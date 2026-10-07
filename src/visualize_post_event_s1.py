import rasterio
import numpy as np
import matplotlib.pyplot as plt


FILES = {
    "VV": "data/raw/sentinel1_20260828_VV.tif",
    "VH": "data/raw/sentinel1_20260828_VH.tif",
}

for polarization, path in FILES.items():

    with rasterio.open(path) as src:
        data = src.read(1)

    data = data.astype(np.float32)
    data[data <= 0] = np.nan

    db = 10 * np.log10(data)

    print()
    print(polarization)
    print("Min:", np.nanmin(db))
    print("1st percentile:", np.nanpercentile(db, 1))
    print("5th percentile:", np.nanpercentile(db, 5))
    print("10th percentile:", np.nanpercentile(db, 10))
    print("Median:", np.nanmedian(db))
    print("90th percentile:", np.nanpercentile(db, 90))
    print("Max:", np.nanmax(db))

    plt.figure(figsize=(10, 8))
    plt.imshow(db, cmap="gray", vmin=-30, vmax=5)
    plt.colorbar(label=f"{polarization} backscatter (dB)")
    plt.title(f"Post-event Sentinel-1 {polarization} - 28 Aug 2026")
    plt.tight_layout()

    output = f"outputs/post_event_{polarization}_db.png"
    plt.savefig(output, dpi=150)
    plt.close()

    print("Saved:", output)