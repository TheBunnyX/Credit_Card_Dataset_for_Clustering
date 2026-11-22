"""Flask app: segment dashboard + prediction API.

Run (from the project root):
    python -m app.app
"""
from flask import Flask, jsonify, render_template, request, send_from_directory

from src.labels import ALGO_INFO, ESSENTIAL_FIELDS, FIELD_INFO, PALETTE
from src.predict import SegmentPredictor

app = Flask(__name__)
_predictor = None


def get_predictor() -> SegmentPredictor:
    global _predictor
    if _predictor is None:
        _predictor = SegmentPredictor()
    return _predictor


@app.errorhandler(FileNotFoundError)
def model_missing(_):
    return jsonify(error="Model not found. Run `python -m src.train` first."), 503


@app.get("/")
def index():
    meta = get_predictor().meta
    segments = meta["segments"]
    total = sum(s["size"] for s in segments.values())
    # largest segment first on the page
    order = sorted(segments, key=lambda c: -segments[c]["size"])
    return render_template(
        "index.html",
        features=meta["feature_columns"],
        essential=ESSENTIAL_FIELDS,
        field_info=FIELD_INFO,
        optional=meta["optional_features"],
        defaults=meta["defaults"],
        segments=segments,
        order=order,
        total=total,
        metrics=meta["metrics"],
        k=meta["k"],
        palette=PALETTE,
        examples=meta["examples"],
        map_points=meta["map"],
        map_variance=meta["map_variance"],
        k_table=meta.get("k_table"),
        algos=meta.get("algo_comparison", {}),
        algo_info=ALGO_INFO,
        data=meta["data_summary"],
    )


@app.get("/favicon.ico")
def favicon():
    # browsers and crawlers request /favicon.ico directly
    return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/api/segments")
def segments():
    meta = get_predictor().meta
    return jsonify(k=meta["k"], metrics=meta["metrics"], segments=meta["segments"])


@app.post("/api/predict")
def predict():
    """Body: one customer object, or {"customers": [ ... ]}.

    Add "fill_missing": true to send only the essential fields; the rest are estimated.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Send a JSON object."), 400
    fill_missing = bool(payload.pop("fill_missing", False))
    records = payload["customers"] if "customers" in payload else [payload]
    if not isinstance(records, list) or not records or not all(isinstance(r, dict) for r in records):
        return jsonify(error="'customers' must be a non-empty list of objects."), 400
    try:
        results = get_predictor().predict(records, fill_missing=fill_missing)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(results=results)


if __name__ == "__main__":
    app.run(debug=True)
