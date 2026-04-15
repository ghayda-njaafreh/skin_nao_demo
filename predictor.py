import json
from inference import predict

DISPLAY_NAMES = {
    "akiec": "Actinic Keratosis / Intraepithelial Carcinoma",
    "bcc": "Basal Cell Carcinoma",
    "bkl": "Benign Keratosis-like Lesion",
    "df": "Dermatofibroma",
    "nv": "Nevus",
    "vasc": "Vascular Lesion",
    "mel": "Melanoma",
}

def load_class_names(labels_path: str = "labels.json") -> list[str]:
    with open(labels_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    labels_dict = {int(k): v for k, v in raw.items()}
    class_names = [labels_dict[i] for i in sorted(labels_dict.keys())]
    return class_names

def get_display_name(code: str) -> str:
    return DISPLAY_NAMES.get(code, code)

def predict_image(
    image_path: str,
    weights_path: str = "model.pth",
    labels_path: str = "labels.json"
) -> dict:
    pred_idx, pred_label, probs = predict(
        image_path=image_path,
        weights_path=weights_path,
        labels_path=labels_path
    )

    class_codes = load_class_names(labels_path)
    probs = [float(p) for p in probs]

    predictions = []
    for i, prob in enumerate(probs):
        class_code = class_codes[i] if i < len(class_codes) else f"class_{i}"
        predictions.append({
            "index": i,
            "class_code": class_code,
            "class_name": get_display_name(class_code),
            "probability": prob
        })

    predictions_sorted = sorted(
        predictions,
        key=lambda x: x["probability"],
        reverse=True
    )

    top_predictions = predictions_sorted[:3]

    return {
        "predicted_index": int(pred_idx),
        "predicted_class_code": str(pred_label),
        "predicted_class_name": get_display_name(str(pred_label)),
        "confidence": float(probs[pred_idx]),
        "top_predictions": top_predictions,
        "all_predictions": predictions_sorted
    }

def build_speech_text(result: dict) -> str:
    top1 = result["top_predictions"][0]
    top2 = result["top_predictions"][1] if len(result["top_predictions"]) > 1 else None

    text = (
        f"The predicted class is {top1['class_name']} "
        f"with {round(top1['probability'] * 100, 1)} percent confidence."
    )

    if top2 and top2["probability"] >= 0.01:
        text += (
            f" Another possible class is {top2['class_name']} "
            f"with {round(top2['probability'] * 100, 1)} percent."
        )

    text += " This result is for educational demonstration only."
    return text