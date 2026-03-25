"""
Optional ML model hub for MediAI.

This module adds:
- Classical ML text classifier (TF-IDF + Logistic Regression)
- Ensemble risk model (RandomForest + GradientBoosting)
- CNN inference hook (TensorFlow/Keras model loader)

All components degrade gracefully when dependencies or trained artifacts
are unavailable.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np


@dataclass
class ModelStatus:
    name: str
    available: bool
    details: str


class MLModelHub:
    """Hybrid ML hub that combines text, risk, and CNN model outputs."""

    def __init__(self) -> None:
        self._statuses: List[ModelStatus] = []
        self.text_pipeline = None
        self.risk_models = {}
        self.cnn_model = None
        self.cnn_labels: List[str] = []

        self._init_text_model()
        self._init_risk_models()
        self._init_cnn_model()

    def _init_text_model(self) -> None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline

            samples = [
                ("high blood sugar frequent urination excessive thirst", "Diabetes Mellitus"),
                ("hba1c elevated glucose fasting sugar high", "Diabetes Mellitus"),
                ("high blood pressure headache dizziness chest pressure", "Hypertension"),
                ("systolic high diastolic high bp severe", "Hypertension"),
                ("low hemoglobin fatigue weakness pallor breathlessness", "Anemia"),
                ("hb low tiredness pale skin anemia", "Anemia"),
                ("tsh high t4 low thyroid weight gain", "Thyroid Disorder"),
                ("thyroid hormone imbalance palpitations cold intolerance", "Thyroid Disorder"),
                ("fever cough sore throat crp elevated opacity", "Respiratory Infection"),
                ("chest infection infiltrate consolidation breathlessness", "Respiratory Infection"),
            ]

            X = [x for x, _ in samples]
            y = [y for _, y in samples]

            pipeline = Pipeline(
                [
                    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                    ("clf", LogisticRegression(max_iter=1200, multi_class="auto")),
                ]
            )
            pipeline.fit(X, y)
            self.text_pipeline = pipeline
            self._statuses.append(ModelStatus("text_classifier", True, "TF-IDF + LogisticRegression"))
        except Exception as exc:
            self.text_pipeline = None
            self._statuses.append(ModelStatus("text_classifier", False, f"Unavailable: {exc}"))

    def _init_risk_models(self) -> None:
        try:
            from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier

            X, y = self._generate_synthetic_risk_data(450)
            rf = RandomForestClassifier(n_estimators=120, random_state=42)
            gb = GradientBoostingClassifier(random_state=42)
            rf.fit(X, y)
            gb.fit(X, y)
            self.risk_models = {"rf": rf, "gb": gb}
            self._statuses.append(ModelStatus("risk_ensemble", True, "RandomForest + GradientBoosting"))
        except Exception as exc:
            self.risk_models = {}
            self._statuses.append(ModelStatus("risk_ensemble", False, f"Unavailable: {exc}"))

    def _init_cnn_model(self) -> None:
        """Load a trained CNN artifact if present.

        Expected artifacts:
        - models/cnn_medical.keras
        - models/cnn_medical.h5
        - models/cnn_labels.json  (list of class labels)
        """
        keras_model_path = os.path.join("models", "cnn_medical.keras")
        h5_model_path = os.path.join("models", "cnn_medical.h5")
        labels_path = os.path.join("models", "cnn_labels.json")

        model_path = ""
        if os.path.exists(keras_model_path):
            model_path = keras_model_path
        elif os.path.exists(h5_model_path):
            model_path = h5_model_path

        if not model_path:
            self._statuses.append(
                ModelStatus(
                    "cnn_classifier",
                    False,
                    "Missing models/cnn_medical.keras or models/cnn_medical.h5 (add trained CNN model to enable)",
                )
            )
            return

        try:
            import tensorflow as tf

            self.cnn_model = tf.keras.models.load_model(model_path)
            if os.path.exists(labels_path):
                with open(labels_path, "r", encoding="utf-8") as f:
                    labels = json.load(f)
                if isinstance(labels, list):
                    self.cnn_labels = [str(x) for x in labels]

            self._statuses.append(ModelStatus("cnn_classifier", True, f"Loaded TensorFlow CNN artifact: {os.path.basename(model_path)}"))
        except Exception as exc:
            self.cnn_model = None
            self._statuses.append(ModelStatus("cnn_classifier", False, f"Unavailable: {exc}"))

    @staticmethod
    def _generate_synthetic_risk_data(size: int) -> Any:
        """Create synthetic features for robust default risk ensemble training."""
        rng = np.random.default_rng(42)
        age = rng.integers(18, 90, size=size)
        symptom_hits = rng.integers(0, 8, size=size)
        critical_hits = rng.integers(0, 4, size=size)
        comorbidity_count = rng.integers(0, 4, size=size)
        top_conf = rng.uniform(0.0, 1.0, size=size)

        raw = (
            (age >= 65).astype(int) * 18
            + symptom_hits * 6
            + critical_hits * 12
            + comorbidity_count * 8
            + (top_conf * 25)
        )

        y = np.where(raw <= 33, 0, np.where(raw <= 66, 1, 2))
        X = np.column_stack([age, symptom_hits, critical_hits, comorbidity_count, top_conf])
        return X, y

    def _predict_text_condition(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = " ".join(
            [
                str(payload.get("symptoms", "")),
                str(payload.get("clinical_text", "")),
                str(payload.get("image_text", "")),
            ]
        ).strip()
        if not self.text_pipeline or not text:
            return {"available": False}

        probs = self.text_pipeline.predict_proba([text])[0]
        classes = list(self.text_pipeline.classes_)
        top_idx = int(np.argmax(probs))
        return {
            "available": True,
            "top_condition": classes[top_idx],
            "confidence": float(probs[top_idx]),
        }

    def _predict_risk_band(self, payload: Dict[str, Any], top_conf: float) -> Dict[str, Any]:
        if not self.risk_models:
            return {"available": False}

        symptoms = str(payload.get("symptoms", "")).lower()
        comorbidities = payload.get("comorbidities") or []
        age = int(payload.get("age") or 30)

        critical_terms = ["chest pain", "shortness of breath", "confusion", "fainting", "severe"]
        critical_hits = sum(1 for t in critical_terms if t in symptoms)
        symptom_hits = len(re.findall(r"[a-zA-Z]{4,}", symptoms)) // 6

        x = np.array(
            [[age, symptom_hits, critical_hits, len(comorbidities), float(top_conf)]],
            dtype=float,
        )

        rf_pred = int(self.risk_models["rf"].predict(x)[0])
        gb_pred = int(self.risk_models["gb"].predict(x)[0])
        voted = int(round((rf_pred + gb_pred) / 2))
        band = {0: "low", 1: "moderate", 2: "high"}.get(voted, "low")

        return {
            "available": True,
            "predictions": {"random_forest": rf_pred, "gradient_boosting": gb_pred},
            "voted_band": band,
        }

    def _predict_cnn(self, image_path: str) -> Dict[str, Any]:
        if not self.cnn_model or not image_path or not os.path.exists(image_path):
            return {"available": False}

        try:
            import tensorflow as tf

            image = tf.keras.utils.load_img(image_path, target_size=(224, 224))
            arr = tf.keras.utils.img_to_array(image)
            arr = np.expand_dims(arr / 255.0, axis=0)

            logits = self.cnn_model.predict(arr, verbose=0)[0]
            top_idx = int(np.argmax(logits))
            top_conf = float(logits[top_idx])
            label = self.cnn_labels[top_idx] if top_idx < len(self.cnn_labels) else f"class_{top_idx}"

            return {
                "available": True,
                "top_label": label,
                "confidence": top_conf,
            }
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    def predict(self, payload: Dict[str, Any], top_conf: float = 0.0) -> Dict[str, Any]:
        text_pred = self._predict_text_condition(payload)
        risk_pred = self._predict_risk_band(payload, top_conf)
        cnn_pred = self._predict_cnn(str(payload.get("image_path", "")))

        condition_votes: Dict[str, float] = {}
        if text_pred.get("available"):
            condition_votes[text_pred["top_condition"]] = float(text_pred.get("confidence", 0.0))

        return {
            "text_classifier": text_pred,
            "risk_ensemble": risk_pred,
            "cnn_classifier": cnn_pred,
            "condition_votes": condition_votes,
            "model_status": [s.__dict__ for s in self._statuses],
        }
