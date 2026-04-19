"""
Binary face-image screening (Autistic vs Non_Autistic).

This now matches the updated Kaggle-Autism project which uses a PyTorch
EfficientNet-B0 transfer-learning classifier.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image

from src.config import FACE_CLASSIFIER_DEFAULT_PATH

# Keras ImageDataGenerator sorts class names alphabetically: Autistic, Non_Autistic
FACE_CLASS_LABELS: Tuple[str, ...] = ("Autistic", "Non_Autistic")
AUTISTIC_CLASS_INDEX = 0


def resolve_face_classifier_path() -> Optional[Path]:
    env = os.getenv("FACE_CLASSIFIER_MODEL_PATH", "").strip()
    if env:
        p = Path(env).expanduser()
        if p.is_file():
            return p
    if FACE_CLASSIFIER_DEFAULT_PATH.is_file():
        return FACE_CLASSIFIER_DEFAULT_PATH
    for name in ("face_asd_classifier.pth",):
        alt = FACE_CLASSIFIER_DEFAULT_PATH.parent / name
        if alt.is_file():
            return alt
    return None


def dev_bypass_face_screening() -> bool:
    return os.getenv("DEV_BYPASS_FACE_SCREENING", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _build_efficientnet_b0(num_classes: int = 2):
    import torch
    from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

    weights = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)
    return model


@lru_cache(maxsize=2)
def _load_torch_checkpoint(path_str: str) -> Dict[str, Any]:
    import torch

    ckpt = torch.load(path_str, map_location="cpu")
    if isinstance(ckpt, dict):
        return ckpt
    raise ValueError("Expected a dict checkpoint (.pth) with model_state and metadata.")


@lru_cache(maxsize=2)
def _load_torch_model(path_str: str):
    import torch

    ckpt = _load_torch_checkpoint(path_str)
    model = _build_efficientnet_b0(num_classes=2)
    state = ckpt.get("model_state") or ckpt.get("state_dict") or ckpt
    model.load_state_dict(state, strict=False)
    model.eval()
    return model


def _torch_preprocess(pil_img: Image.Image):
    from torchvision.models import EfficientNet_B0_Weights

    preprocess = EfficientNet_B0_Weights.DEFAULT.transforms()
    return preprocess(pil_img.convert("RGB")).unsqueeze(0)


def predict_face_binary(pil_img: Image.Image) -> Dict[str, Any]:
    """
    Returns dict with probabilities, predicted label, and is_autistic (True => continue app).
    """
    path = resolve_face_classifier_path()
    if path is None:
        raise FileNotFoundError(
            "Face classifier weights not found. Place your trained .pth at "
            f"{FACE_CLASSIFIER_DEFAULT_PATH} or set environment variable "
            "FACE_CLASSIFIER_MODEL_PATH to the full file path."
        )

    import torch

    model = _load_torch_model(str(path.resolve()))
    x = _torch_preprocess(pil_img)
    with torch.no_grad():
        logits = model(x)
        probs_t = torch.softmax(logits, dim=1)[0]
    probs = probs_t.detach().cpu().numpy()
    class_idx = int(probs.argmax())
    predicted_label = FACE_CLASS_LABELS[class_idx]
    is_autistic = class_idx == AUTISTIC_CLASS_INDEX

    return {
        "predicted_class_index": class_idx,
        "predicted_label": predicted_label,
        "is_autistic": is_autistic,
        "probabilities": {
            FACE_CLASS_LABELS[i]: float(probs[i]) for i in range(len(FACE_CLASS_LABELS))
        },
        "model_path": str(path),
    }


def predict_face_binary_or_bypass(pil_img: Optional[Image.Image]) -> Dict[str, Any]:
    """
    If DEV_BYPASS_FACE_SCREENING is set, returns a synthetic 'autistic' result without loading TF.
    Otherwise requires pil_img and runs the classifier.
    """
    if dev_bypass_face_screening():
        return {
            "predicted_class_index": AUTISTIC_CLASS_INDEX,
            "predicted_label": FACE_CLASS_LABELS[AUTISTIC_CLASS_INDEX],
            "is_autistic": True,
            "probabilities": {FACE_CLASS_LABELS[0]: 1.0, FACE_CLASS_LABELS[1]: 0.0},
            "model_path": None,
            "dev_bypass": True,
        }
    if pil_img is None:
        raise ValueError("Image is required when DEV_BYPASS_FACE_SCREENING is not enabled.")
    return predict_face_binary(pil_img)
