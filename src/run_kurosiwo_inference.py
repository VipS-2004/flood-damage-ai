import sys
from pathlib import Path

import numpy as np
import rasterio
import torch

sys.path.insert(0, "KuroSiwo")

from models.snunet import SNUNet_ECAM


DATA_DIR = Path("data/raw")
MODEL_PATH = Path("KuroSiwo/best_segmentation.pt")
OUTPUT_PATH = Path("outputs/kurosiwo_flood_mask.tif")

BEFORE_DATE = "20260816"
AFTER_DATE = "20260828"

CLAMP_MAX = 0.15


def load_band(date, polarization):
    path = DATA_DIR / f"sentinel1_{date}_{polarization}.tif"

    with rasterio.open(path) as src:
        image = src.read(1).astype(np.float32)
        profile = src.profile.copy()

    return image, profile


def make_input(date):
    vv, _ = load_band(date, "VV")
    vh, _ = load_band(date, "VH")

    ratio = vh / (vv + 1e-7)

    image = np.stack([vv, vh, ratio], axis=0)

    image = np.clip(image, 0.0, CLAMP_MAX)

    image = np.nan_to_num(
        image,
        nan=CLAMP_MAX,
        posinf=CLAMP_MAX,
        neginf=0.0,
    )

    return torch.from_numpy(image).float()


def main():
    print("Loading Sentinel-1 inputs...")

    before = make_input(BEFORE_DATE)
    after = make_input(AFTER_DATE)

    print("Before shape:", tuple(before.shape))
    print("After shape:", tuple(after.shape))

    print("Before range:", before.min().item(), before.max().item())
    print("After range:", after.min().item(), after.max().item())

    height, width = before.shape[1:]

    padded_height = int(np.ceil(height / 16) * 16)
    padded_width = int(np.ceil(width / 16) * 16)

    pad_bottom = padded_height - height
    pad_right = padded_width - width

    before = torch.nn.functional.pad(
        before,
        (0, pad_right, 0, pad_bottom),
        mode="replicate",
    )

    after = torch.nn.functional.pad(
        after,
        (0, pad_right, 0, pad_bottom),
        mode="replicate",
    )

    print("Padded shape:", tuple(before.shape))

    model = SNUNet_ECAM(
        in_channels=3,
        out_ch=3,
        base_channel=32,
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location="cpu",
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print("Model loaded.")

    with torch.no_grad():
        logits = model(
            before.unsqueeze(0),
            after.unsqueeze(0),
        )

        prediction = torch.argmax(logits, dim=1)[0]

    prediction = prediction[:height, :width].numpy().astype(np.uint8)

    unique, counts = np.unique(prediction, return_counts=True)

    total = prediction.size

    print()
    print("Prediction distribution:")

    labels = {
        0: "No water",
        1: "Permanent water",
        2: "Flood",
    }

    for value, count in zip(unique, counts):
        percentage = count / total * 100

        print(
            f"{value} ({labels.get(value, 'Unknown')}): "
            f"{count} pixels ({percentage:.2f}%)"
        )

    with rasterio.open(
        DATA_DIR / f"sentinel1_{BEFORE_DATE}_VV.tif"
    ) as src:
        profile = src.profile.copy()

    profile.update(
        dtype=rasterio.uint8,
        count=1,
        compress="lzw",
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(OUTPUT_PATH, "w", **profile) as dst:
        dst.write(prediction, 1)

    print()
    print("Saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()