import pytest

from src.preprocess import MODEL_DIR

pytestmark = pytest.mark.skipif(
    not (MODEL_DIR / "pipeline.joblib").exists(), reason="run `python -m src.train` first"
)


@pytest.fixture(scope="module")
def predictor():
    from src.predict import SegmentPredictor

    return SegmentPredictor()


def test_each_example_customer_lands_in_its_own_segment(predictor):
    for cid, example in predictor.meta["examples"].items():
        assert predictor.predict([example])[0]["cluster"] == int(cid)


def test_simple_mode_fills_advanced_fields(predictor):
    essentials = {
        "BALANCE": 1200, "CREDIT_LIMIT": 3000, "PURCHASES": 300, "PURCHASES_FREQUENCY": 0.5,
        "CASH_ADVANCE": 0, "CASH_ADVANCE_FREQUENCY": 0, "PAYMENTS": 800, "PRC_FULL_PAYMENT": 0.1,
    }
    r = predictor.predict([essentials], fill_missing=True)[0]
    assert r["segment_th"] and 0 <= r["confidence"] <= 1
    with pytest.raises(ValueError):
        predictor.predict([essentials])  # strict mode still requires every field


def test_negative_values_rejected(predictor):
    example = dict(next(iter(predictor.meta["examples"].values())), BALANCE=-5)
    with pytest.raises(ValueError):
        predictor.predict([example])


def test_reasons_point_the_right_way(predictor):
    cash_heavy = {
        "BALANCE": 3000, "CREDIT_LIMIT": 4000, "PURCHASES": 0, "PURCHASES_FREQUENCY": 0,
        "CASH_ADVANCE": 5000, "CASH_ADVANCE_FREQUENCY": 0.5, "PAYMENTS": 1500, "PRC_FULL_PAYMENT": 0,
    }
    r = predictor.predict([cash_heavy], fill_missing=True)[0]
    texts = " ".join(x["text"] for x in r["reasons"])
    assert "ยอดกดเงินสดสูง" in texts
