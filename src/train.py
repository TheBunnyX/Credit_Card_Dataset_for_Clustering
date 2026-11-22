"""Train the segmentation pipeline.

Usage:
    python -m src.train            # choose k automatically (silhouette, k=3..8)
    python -m src.train --k 5      # fix k
"""
import argparse
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.pipeline import Pipeline

from src.evaluation import compare_algorithms, hopkins_vs_null
from src.preprocess import (
    MODEL_DIR,
    OPTIONAL_FEATURES,
    RAW_FEATURES,
    ROOT,
    build_preprocessor,
    load_data,
)
from src.segments import profile_clusters
from src.ui_data import build_ui_assets

SEED = 42


def bootstrap_stability(X, k: int, n: int = 5, frac: float = 0.8) -> float:
    """Mean ARI between a full fit and fits on random 80% subsamples (1.0 = identical)."""
    rng = np.random.RandomState(SEED)
    full = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(X)
    scores = []
    for i in range(n):
        idx = rng.choice(len(X), int(frac * len(X)), replace=False)
        sub = KMeans(n_clusters=k, n_init=10, random_state=SEED + i + 1).fit(X[idx])
        scores.append(adjusted_rand_score(full.labels_[idx], sub.labels_))
    return float(np.mean(scores))


def select_k(X, k_range=range(3, 9), min_share: float = 0.02) -> tuple[int, pd.DataFrame]:
    """Pick k by rank-averaging silhouette, Davies-Bouldin and bootstrap stability.

    Silhouette alone is nearly flat on this data (~0.21-0.23), so it cannot decide k.
    Candidates with a cluster smaller than `min_share` of customers are excluded.
    """
    rows = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(X)
        rows.append(
            {
                "k": k,
                "silhouette": silhouette_score(X, km.labels_, sample_size=5000, random_state=SEED),
                "davies_bouldin": davies_bouldin_score(X, km.labels_),
                "stability": bootstrap_stability(X, k),
                "min_share": np.bincount(km.labels_).min() / len(X),
            }
        )
    table = pd.DataFrame(rows)
    table["rank_score"] = (
        table["silhouette"].rank(ascending=False)
        + table["davies_bouldin"].rank(ascending=True)
        + table["stability"].rank(ascending=False)
    )
    eligible = table[table["min_share"] >= min_share]
    # ties on rank_score are broken by the higher silhouette
    best = eligible.sort_values(["rank_score", "silhouette"], ascending=[True, False]).iloc[0]
    return int(best["k"]), table


def main(k: int | None = None) -> None:
    raw = load_data()
    prep = build_preprocessor()
    X = prep.fit_transform(raw)

    table = None
    if k is None:
        k, table = select_k(X)
        print(table.round(3).to_string(index=False))
        print("(rank_score: lower is better)")
        print(f"-> selected k = {k}")

    pipeline = Pipeline(
        prep.steps + [("model", KMeans(n_clusters=k, n_init=20, random_state=SEED))]
    ).fit(raw)
    labels = pipeline.named_steps["model"].labels_
    X = pipeline[:-1].transform(raw)

    metrics = {
        "silhouette": round(float(silhouette_score(X, labels, sample_size=5000, random_state=SEED)), 4),
        "davies_bouldin": round(float(davies_bouldin_score(X, labels)), 4),
        "calinski_harabasz": round(float(calinski_harabasz_score(X, labels)), 2),
        "stability_ari": round(bootstrap_stability(X, k), 4),
        "pca_components": int(X.shape[1]),
        **hopkins_vs_null(X),
    }
    print("metrics:", metrics)

    segments = profile_clusters(raw, labels)
    meta = {
        "k": k,
        "metrics": metrics,
        "feature_columns": RAW_FEATURES,
        "optional_features": OPTIONAL_FEATURES,
        "defaults": {c: round(float(raw[c].median()), 3) for c in RAW_FEATURES},
        "segments": segments,
        "map_variance": round(float(pipeline.named_steps["pca"].explained_variance_ratio_[:2].sum()), 3),
        "k_table": None if table is None else table.round(3).to_dict(orient="records"),
        "algo_comparison": compare_algorithms(X, k),
        **build_ui_assets(raw, X, labels, pipeline.named_steps["model"].cluster_centers_),
    }

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_DIR / "pipeline.joblib")
    (MODEL_DIR / "segments.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    out = raw.copy()
    out["CLUSTER"] = labels
    out["SEGMENT"] = out["CLUSTER"].astype(str).map(lambda c: segments[c]["name"])
    out_path = ROOT / "data" / "processed" / "customers_segmented.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    print("\nSegments:")
    for cid, s in segments.items():
        print(f"  [{cid}] {s['name']:<28} {s['size']:>5} customers ({s['share']:.1%})")
    print(f"\nSaved model to {MODEL_DIR}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=None, help="number of clusters (default: auto)")
    main(ap.parse_args().k)
