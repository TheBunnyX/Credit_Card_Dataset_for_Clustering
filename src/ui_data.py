"""Extra artefacts saved next to the model so the web UI can explain itself."""
import numpy as np
import pandas as pd

from src.labels import REASON_LABELS
from src.preprocess import RAW_FEATURES, engineer_features


def build_ui_assets(raw: pd.DataFrame, X: np.ndarray, labels: np.ndarray, centers: np.ndarray, seed: int = 42) -> dict:
    # One real, typical customer per segment (closest to the centroid) -> "try an example" buttons
    examples = {}
    for c in range(len(centers)):
        idx = np.where(labels == c)[0]
        nearest = idx[np.linalg.norm(X[idx] - centers[c], axis=1).argmin()]
        row = raw.iloc[nearest]
        examples[str(c)] = {col: (None if pd.isna(row[col]) else round(float(row[col]), 3)) for col in RAW_FEATURES}

    # Sample of customers on the first two principal components -> customer map
    rng = np.random.RandomState(seed)
    sample = rng.choice(len(X), size=min(1500, len(X)), replace=False)
    map_points = [[round(float(X[i, 0]), 2), round(float(X[i, 1]), 2), int(labels[i])] for i in sample]

    # Percentile tables -> "higher than X% of customers" explanations
    percentiles = {c: np.percentile(raw[c].dropna(), np.arange(0, 101)).round(3).tolist() for c in REASON_LABELS}

    # Typical transaction sizes -> fill the advanced fields in simple mode
    buys = raw[raw["PURCHASES_TRX"] > 0]
    cash = raw[raw["CASH_ADVANCE_TRX"] > 0]
    derive = {
        "avg_purchase": round(float((buys["PURCHASES"] / buys["PURCHASES_TRX"]).median()), 2),
        "avg_cash_advance": round(float((cash["CASH_ADVANCE"] / cash["CASH_ADVANCE_TRX"]).median()), 2),
        "balance_frequency": round(float(raw["BALANCE_FREQUENCY"].median()), 3),
        "tenure": int(raw["TENURE"].median()),
    }
    data_summary = {
        "rows": int(len(raw)),
        "columns": len(RAW_FEATURES),
        "missing": {c: int(n) for c, n in raw[RAW_FEATURES].isna().sum().items() if n > 0},
        "model_features": int(engineer_features(raw.head(1)).shape[1]),  # after feature engineering
        "pca_dimensions": int(X.shape[1]),
    }
    return {
        "examples": examples,
        "map": map_points,
        "percentiles": percentiles,
        "derive": derive,
        "data_summary": data_summary,
    }
