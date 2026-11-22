import numpy as np
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline

from src.preprocess import RAW_FEATURES, build_preprocessor, load_data


def _fit(k=4):
    raw = load_data()
    pipe = Pipeline(build_preprocessor().steps + [("model", KMeans(n_clusters=k, n_init=3, random_state=0))])
    return raw, pipe.fit(raw)


def test_preprocessing_has_no_nan_or_inf():
    raw = load_data()
    X = build_preprocessor().fit_transform(raw)
    assert X.shape[0] == len(raw)
    assert np.isfinite(X).all()


def test_pipeline_predicts_valid_cluster():
    raw, pipe = _fit(4)
    labels = pipe.predict(raw.head(20))
    assert set(labels) <= set(range(4))


def test_optional_fields_can_be_missing():
    raw, pipe = _fit(3)
    row = raw[RAW_FEATURES].head(1).copy()
    row["MINIMUM_PAYMENTS"] = np.nan
    row["CREDIT_LIMIT"] = np.nan
    assert len(pipe.predict(row)) == 1
