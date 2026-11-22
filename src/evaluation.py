"""Clustering-quality helpers shared by train.py and the notebook."""
import numpy as np
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score, davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors


def compare_algorithms(X, k: int, seed: int = 42, n_boot: int = 3) -> dict:
    """Score the candidate algorithms on the same data with the same k (DBSCAN picks its own).

    stability = mean ARI between the full fit and fits on random 80% subsamples, compared on
    the shared customers. Silhouette / DB for DBSCAN exclude the points it labels as noise.
    """
    X = np.asarray(X)
    rng = np.random.RandomState(seed)
    subsets = [np.sort(rng.choice(len(X), int(0.8 * len(X)), replace=False)) for _ in range(n_boot)]
    makers = {
        "kmeans": lambda s: KMeans(n_clusters=k, n_init=10, random_state=s),
        "hierarchical": lambda s: AgglomerativeClustering(n_clusters=k, linkage="ward"),
        "gmm": lambda s: GaussianMixture(n_components=k, covariance_type="full", random_state=s),
        "dbscan": lambda s: DBSCAN(eps=1.5, min_samples=30),
    }
    results = {}
    for name, make in makers.items():
        full = make(seed).fit_predict(X)
        stability = np.mean([
            adjusted_rand_score(full[idx], make(seed + i + 1).fit_predict(X[idx]))
            for i, idx in enumerate(subsets)
        ])
        mask = full != -1
        labs = full[mask]
        n_clusters = len(set(labs))
        sil = db = None
        if n_clusters > 1:
            sil = round(float(silhouette_score(X[mask], labs, sample_size=5000, random_state=seed)), 3)
            db = round(float(davies_bouldin_score(X[mask], labs)), 2)
        sizes = np.unique(labs, return_counts=True)[1] if n_clusters else np.array([0])
        results[name] = {
            "clusters": int(n_clusters),
            "noise_share": round(float(1 - mask.mean()), 3),
            "min_share": round(float(sizes.min() / len(X)), 3),
            "silhouette": sil,
            "davies_bouldin": db,
            "stability": round(float(stability), 3),
            "can_predict": name in ("kmeans", "gmm"),
        }
    return results


def hopkins(X, m_frac: float = 0.1, seed: int = 0) -> float:
    """Hopkins statistic: ~0.5 = uniform/random, -> 1 = clusterable.

    Compares nearest-neighbour distances of uniform random points (u) with those of
    real sampled points (w): H = sum(u) / (sum(u) + sum(w)).
    """
    rng = np.random.RandomState(seed)
    X = np.asarray(X, dtype=float)
    n, d = X.shape
    m = max(1, int(m_frac * n))
    nn = NearestNeighbors(n_neighbors=2).fit(X)
    u = nn.kneighbors(rng.uniform(X.min(0), X.max(0), size=(m, d)), n_neighbors=1)[0][:, 0]
    w = nn.kneighbors(X[rng.choice(n, m, replace=False)], n_neighbors=2)[0][:, 1]
    return float(u.sum() / (u.sum() + w.sum()))


def hopkins_vs_null(X, repeats: int = 5) -> dict:
    """Hopkins on the data and on a column-shuffled copy (same marginals, no structure).

    A raw Hopkins value near 0.95+ is NOT evidence of clusters by itself: on heavily
    skewed data the shuffled copy scores almost as high. Only the gap is meaningful.
    """
    X = np.asarray(X, dtype=float)
    real, null = [], []
    for s in range(repeats):
        rng = np.random.RandomState(100 + s)
        shuffled = np.column_stack([rng.permutation(col) for col in X.T])
        real.append(hopkins(X, seed=s))
        null.append(hopkins(shuffled, seed=s))
    return {
        "hopkins": round(float(np.mean(real)), 4),
        "hopkins_null": round(float(np.mean(null)), 4),
        "hopkins_gap": round(float(np.mean(real) - np.mean(null)), 4),
    }
