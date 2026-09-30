"""
Loads the trained career-cluster classifier and scores a profile
against it. Import `predict_clusters` from here in the Flask app.
"""

import json
import os

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "career_classifier.keras")
LABELS_PATH = os.path.join(MODEL_DIR, "labels.json")

_model = None
_labels = None


class ModelNotTrainedError(RuntimeError):
    pass


def _load():
    global _model, _labels
    if _model is not None:
        return
    if not os.path.exists(MODEL_PATH) or not os.path.exists(LABELS_PATH):
        raise ModelNotTrainedError(
            "No trained model found. Run `python -m model.train_classifier` "
            "first, then restart the app."
        )
    # Imported lazily so `python -m model.train_classifier` and app
    # startup both work without forcing TensorFlow to load twice.
    import tensorflow as tf

    _model = tf.keras.models.load_model(MODEL_PATH)
    with open(LABELS_PATH) as f:
        _labels = json.load(f)


def predict_clusters(skills, interests, top_k=3):
    """
    skills, interests: lists of strings.
    Returns a list of (category_name, confidence) tuples, highest first.
    """
    _load()
    text = " ".join(skills) + " " + " ".join(interests)
    text = text.strip() or "general interest exploring career options"

    import tensorflow as tf

    probs = _model.predict(tf.constant([text]), verbose=0)[0]
    ranked = sorted(zip(_labels, probs), key=lambda x: x[1], reverse=True)
    return [(label, float(score)) for label, score in ranked[:top_k]]
