"""
Trains a small TensorFlow/Keras text classifier that maps a profile's
skills + interests to one of the predefined career clusters
(data/training_data.py). This narrows the search space before the LLM
step writes the specific job roles, rationale and learning paths -
TensorFlow is doing the thing it's actually good at (fast, cheap
classification over structured categories), while the open-ended
reasoning is left to the language model.

Run this once before starting the app:

    python -m model.train_classifier

It writes two files:
    model/career_classifier.keras   - the trained model (includes text
                                       vectorization, so no separate
                                       tokenizer file is needed)
    model/labels.json                - the ordered list of category
                                       names the model's output indices
                                       correspond to
"""

import json
import os

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

from data.training_data import CATEGORIES, TRAINING_DATA

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "career_classifier.keras")
LABELS_PATH = os.path.join(MODEL_DIR, "labels.json")

MAX_TOKENS = 2000
SEQUENCE_LENGTH = 40
EMBEDDING_DIM = 32


def build_model(texts):
    vectorizer = layers.TextVectorization(
        max_tokens=MAX_TOKENS,
        output_mode="int",
        output_sequence_length=SEQUENCE_LENGTH,
    )
    vectorizer.adapt(texts)

    model = tf.keras.Sequential([
        layers.Input(shape=(1,), dtype=tf.string),
        vectorizer,
        layers.Embedding(MAX_TOKENS, EMBEDDING_DIM, mask_zero=True),
        layers.GlobalAveragePooling1D(),
        layers.Dense(32, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(len(CATEGORIES), activation="softmax"),
    ])
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    texts = np.array([t for t, _ in TRAINING_DATA])
    label_to_idx = {c: i for i, c in enumerate(CATEGORIES)}
    labels = np.array([label_to_idx[c] for _, c in TRAINING_DATA])

    model = build_model(texts)
    print(model.summary())

    # Keras 3's multi-backend fit() is picky about raw numpy string
    # arrays - route through tf.data instead, which handles tf.string
    # tensors cleanly regardless of backend.
    dataset = tf.data.Dataset.from_tensor_slices((texts, labels)).shuffle(
        len(texts), seed=42
    ).batch(8)

    model.fit(dataset, epochs=60, verbose=2)

    model.save(MODEL_PATH)
    with open(LABELS_PATH, "w") as f:
        json.dump(CATEGORIES, f, indent=2)

    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved labels to {LABELS_PATH}")


if __name__ == "__main__":
    main()
