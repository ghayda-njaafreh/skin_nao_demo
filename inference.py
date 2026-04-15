import argparse
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from model import load_model


def load_labels(labels_path: str = "labels.json") -> dict[int, str]:
    labels_file = Path(labels_path)
    if not labels_file.exists():
        raise FileNotFoundError(f"labels.json not found at: {labels_file}")

    with labels_file.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    return {int(k): v for k, v in raw.items()}


def preprocess_image(image_path: str) -> torch.Tensor:
    img_file = Path(image_path)
    if not img_file.exists():
        raise FileNotFoundError(f"Image not found at: {img_file}")

    img = Image.open(img_file).convert("RGB")
    img = img.resize((28, 28))

    arr = np.array(img).astype("float32") / 255.0  # [H, W, C] in [0,1]
    arr = np.transpose(arr, (2, 0, 1))            # [C, H, W]
    tensor = torch.from_numpy(arr).unsqueeze(0)   # [1, 3, 28, 28]

    return tensor


def predict(
    image_path: str,
    weights_path: str = "model.pth",
    labels_path: str = "labels.json"
):
    model, device = load_model(weights_path)
    id2label = load_labels(labels_path)

    x = preprocess_image(image_path).to(device)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]

    pred_idx = int(torch.argmax(probs).item())
    pred_label = id2label.get(pred_idx, str(pred_idx))
    probs_list = probs.cpu().tolist()

    return pred_idx, pred_label, probs_list


def main():
    parser = argparse.ArgumentParser(
        description="Run inference with SkinCNN on a dermatoscopic image."
    )
    parser.add_argument("image", type=str, help="Path to input dermatoscopic image.")
    parser.add_argument(
        "--weights",
        type=str,
        default="model.pth",
        help="Path to model weights (.pth).",
    )
    parser.add_argument(
        "--labels",
        type=str,
        default="labels.json",
        help="Path to labels.json.",
    )
    args = parser.parse_args()

    idx, label, probs = predict(
        image_path=args.image,
        weights_path=args.weights,
        labels_path=args.labels,
    )

    print(f"Predicted class index: {idx}")
    print(f"Predicted label      : {label}")
    print(f"Probabilities        : {probs}")


if __name__ == "__main__":
    main()