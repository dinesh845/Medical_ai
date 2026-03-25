"""
Train a CNN image classifier for MediAI and export model artifacts.

Expected dataset layout:
dataset/
  class_a/
    img1.jpg
    ...
  class_b/
    img2.jpg
    ...

Output artifacts:
- models/cnn_medical.keras
- models/cnn_medical.h5
- models/cnn_labels.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import tempfile
from pathlib import Path
from statistics import mean


def _collect_class_counts(dataset_dir: str) -> dict:
    root = Path(dataset_dir)
    counts = {}
    for class_dir in sorted([d for d in root.iterdir() if d.is_dir()]):
        image_files = [
            p
            for p in class_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        counts[class_dir.name] = len(image_files)
    return counts


def _build_balanced_dataset(dataset_dir: str, target_per_class: int | None = None, seed: int = 42) -> str:
    """Create a temporary balanced dataset directory.

    - Majority classes are downsampled.
    - Minority classes are upsampled via repeated file sampling.
    """
    rng = random.Random(seed)
    root = Path(dataset_dir)
    class_dirs = [d for d in root.iterdir() if d.is_dir()]
    if not class_dirs:
        raise ValueError(f"No class folders found in dataset: {dataset_dir}")

    counts = _collect_class_counts(dataset_dir)
    non_zero = [c for c in counts.values() if c > 0]
    if len(non_zero) < 2:
        raise ValueError("Need at least 2 non-empty classes to train a CNN model.")

    if target_per_class is None:
        target_per_class = max(8, int(round(mean(non_zero))))

    balanced_root = Path(tempfile.mkdtemp(prefix="balanced_dataset_"))
    print(f"Balancing dataset to target_per_class={target_per_class}")

    for class_dir in class_dirs:
        class_name = class_dir.name
        class_images = [
            p
            for p in class_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        if not class_images:
            continue

        if len(class_images) >= target_per_class:
            selected = rng.sample(class_images, target_per_class)
        else:
            selected = [rng.choice(class_images) for _ in range(target_per_class)]

        out_class_dir = balanced_root / class_name
        out_class_dir.mkdir(parents=True, exist_ok=True)

        for idx, src in enumerate(selected):
            dst = out_class_dir / f"{src.stem}_{idx}{src.suffix.lower()}"
            shutil.copy2(src, dst)

    return str(balanced_root)


def train(
    dataset_dir: str,
    epochs: int = 12,
    batch_size: int = 16,
    target_per_class: int | None = None,
) -> None:
    import tensorflow as tf

    if not os.path.isdir(dataset_dir):
        raise ValueError(f"Dataset directory not found: {dataset_dir}")

    original_counts = _collect_class_counts(dataset_dir)
    print(f"Original class counts: {original_counts}")

    balanced_dataset_dir = _build_balanced_dataset(
        dataset_dir,
        target_per_class=target_per_class,
        seed=42,
    )
    balanced_counts = _collect_class_counts(balanced_dataset_dir)
    print(f"Balanced class counts: {balanced_counts}")

    img_size = (224, 224)
    train_ds = tf.keras.utils.image_dataset_from_directory(
        balanced_dataset_dir,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=img_size,
        batch_size=batch_size,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        balanced_dataset_dir,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=img_size,
        batch_size=batch_size,
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    if num_classes < 2:
        raise ValueError("Need at least 2 classes to train a CNN model.")

    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.12),
            tf.keras.layers.RandomTranslation(0.08, 0.08),
            tf.keras.layers.RandomContrast(0.15),
        ],
        name="augmentation",
    )

    normalization = tf.keras.layers.Rescaling(1.0 / 255)
    train_ds = train_ds.map(lambda x, y: (augmentation(normalization(x), training=True), y)).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: (normalization(x), y)).prefetch(tf.data.AUTOTUNE)

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    model = tf.keras.Sequential(
        [
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.SparseTopKCategoricalAccuracy(k=2, name="top2_accuracy")],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6),
    ]

    model.fit(train_ds, validation_data=val_ds, epochs=epochs, verbose=1, callbacks=callbacks)

    os.makedirs("models", exist_ok=True)
    model.save(os.path.join("models", "cnn_medical.keras"))
    model.save(os.path.join("models", "cnn_medical.h5"))
    with open(os.path.join("models", "cnn_labels.json"), "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)

    print("Saved models/cnn_medical.keras, models/cnn_medical.h5 and models/cnn_labels.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CNN model for MediAI")
    parser.add_argument("--dataset", required=True, help="Path to image dataset directory")
    parser.add_argument("--epochs", type=int, default=12, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument(
        "--target-per-class",
        type=int,
        default=None,
        help="Balanced samples per class (default: auto based on class distribution)",
    )
    args = parser.parse_args()

    train(
        args.dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        target_per_class=args.target_per_class,
    )


if __name__ == "__main__":
    main()
