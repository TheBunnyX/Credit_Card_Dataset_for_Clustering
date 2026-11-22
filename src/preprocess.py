"""Data loading, feature engineering and preprocessing pipeline.

Everything here is stateless or lives inside an sklearn Pipeline so the exact
same transformation is applied at training time and at inference time (Flask).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "CCGENERAL.csv"
MODEL_DIR = ROOT / "models"

ID_COL = "CUST_ID"
PCA_VARIANCE = 0.90

# The 16 behavioural columns of the dataset (CUST_ID excluded).
RAW_FEATURES = [
    "BALANCE",
    "BALANCE_FREQUENCY",
    "PURCHASES",
    "ONEOFF_PURCHASES",
    "INSTALLMENTS_PURCHASES",
    "CASH_ADVANCE",
    "PURCHASES_FREQUENCY",
    "ONEOFF_PURCHASES_FREQUENCY",
    "PURCHASES_INSTALLMENTS_FREQUENCY",
    "CASH_ADVANCE_FREQUENCY",
    "CASH_ADVANCE_TRX",
    "PURCHASES_TRX",
    "CREDIT_LIMIT",
    "PAYMENTS",
    "MINIMUM_PAYMENTS",
    "PRC_FULL_PAYMENT",
    "TENURE",
]

# Columns that may be left empty by the user / contain NaN in the raw data.
OPTIONAL_FEATURES = ["MINIMUM_PAYMENTS", "CREDIT_LIMIT"]

# Heavily right-skewed amount/count columns -> log1p.
LOG_COLS = [
    "BALANCE",
    "PURCHASES",
    "ONEOFF_PURCHASES",
    "INSTALLMENTS_PURCHASES",
    "CASH_ADVANCE",
    "CASH_ADVANCE_TRX",
    "PURCHASES_TRX",
    "CREDIT_LIMIT",
    "PAYMENTS",
    "MINIMUM_PAYMENTS",
]


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def _ratio(a: pd.Series, b: pd.Series) -> pd.Series:
    """a / b; 0 when b == 0; NaN when b is NaN (imputed later)."""
    r = a / b.where(b > 0)
    return r.mask(b == 0, 0.0)


def engineer_features(X) -> pd.DataFrame:
    """Raw customer rows -> model-ready numeric frame (still may contain NaN)."""
    df = pd.DataFrame(X).reindex(columns=RAW_FEATURES)
    df = df.apply(pd.to_numeric, errors="coerce")

    out = pd.DataFrame(index=df.index)
    out["MIN_PAYMENTS_MISSING"] = df["MINIMUM_PAYMENTS"].isna().astype(float)

    # Engineered behaviour ratios
    out["PAYMENT_RATIO"] = _ratio(df["PAYMENTS"], df["BALANCE"] + 1)
    out["CREDIT_UTILIZATION"] = _ratio(df["BALANCE"], df["CREDIT_LIMIT"])
    out["AVG_PURCHASE"] = _ratio(df["PURCHASES"], df["PURCHASES_TRX"])
    out["AVG_CASH_ADVANCE"] = _ratio(df["CASH_ADVANCE"], df["CASH_ADVANCE_TRX"])

    for col in RAW_FEATURES:
        if col in LOG_COLS:
            out[col] = np.log1p(df[col].clip(lower=0))
        else:
            out[col] = df[col]

    for col in ["PAYMENT_RATIO", "CREDIT_UTILIZATION", "AVG_PURCHASE", "AVG_CASH_ADVANCE"]:
        out[col] = np.log1p(out[col].clip(lower=0))
    return out


def build_preprocessor(pca_variance: float | None = PCA_VARIANCE) -> Pipeline:
    """features -> median imputation -> standard scaling -> PCA (denoising).

    PCA keeps `pca_variance` of the variance (22 -> ~9 dims). In experiments it gave
    tighter clusters (Davies-Bouldin 1.49 -> 1.35) and the most stable K-Means result,
    without lowering silhouette measured in the original feature space.
    """
    steps = [
        ("features", FunctionTransformer(engineer_features, validate=False)),
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
    if pca_variance:
        steps.append(("pca", PCA(n_components=pca_variance, random_state=0)))
    return Pipeline(steps)
