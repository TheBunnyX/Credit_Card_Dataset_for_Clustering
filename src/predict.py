"""Inference helper used by the Flask app (and usable from scripts)."""
import json
import math

import joblib
import numpy as np
import pandas as pd

from src.labels import REASON_LABELS
from src.preprocess import MODEL_DIR


class SegmentPredictor:
    def __init__(self, model_dir=MODEL_DIR):
        self.pipeline = joblib.load(model_dir / "pipeline.joblib")
        self.meta = json.loads((model_dir / "segments.json").read_text(encoding="utf-8"))
        self.features = self.meta["feature_columns"]
        self.optional = set(self.meta["optional_features"])

    @staticmethod
    def _blank(val) -> bool:
        return val is None or (isinstance(val, str) and not val.strip())

    def _complete(self, rec: dict) -> dict:
        """Simple mode: estimate the less-known fields from the essential ones."""
        d = self.meta["derive"]
        rec = dict(rec)

        def num(key):
            try:
                return float(rec[key]) if not self._blank(rec.get(key)) else 0.0
            except (TypeError, ValueError):
                return 0.0  # real validation happens later with a clear message

        purchases, cash = num("PURCHASES"), num("CASH_ADVANCE")
        freq = num("PURCHASES_FREQUENCY")
        guesses = {
            "ONEOFF_PURCHASES": purchases * 0.5,
            "INSTALLMENTS_PURCHASES": purchases * 0.5,
            "ONEOFF_PURCHASES_FREQUENCY": freq * 0.5,
            "PURCHASES_INSTALLMENTS_FREQUENCY": freq * 0.5,
            "PURCHASES_TRX": 0 if purchases <= 0 else max(1, round(purchases / d["avg_purchase"])),
            "CASH_ADVANCE_TRX": 0 if cash <= 0 else max(1, round(cash / d["avg_cash_advance"])),
            "BALANCE_FREQUENCY": d["balance_frequency"],
            "TENURE": d["tenure"],
        }
        for key, val in guesses.items():
            if self._blank(rec.get(key)):
                rec[key] = val
        return rec

    def _to_frame(self, records: list[dict], fill_missing: bool = False) -> pd.DataFrame:
        rows = []
        for i, rec in enumerate(records):
            if fill_missing:
                rec = self._complete(rec)
            row, missing = {}, []
            for col in self.features:
                val = rec.get(col)
                if self._blank(val):
                    if col not in self.optional:
                        missing.append(col)
                    row[col] = float("nan")
                    continue
                try:
                    num = float(val)
                except (TypeError, ValueError):
                    raise ValueError(f"record {i}: '{col}' must be a number, got {val!r}")
                if math.isnan(num) or math.isinf(num):
                    raise ValueError(f"record {i}: '{col}' must be a finite number")
                if num < 0:
                    raise ValueError(f"record {i}: '{col}' must not be negative")
                row[col] = num
            if missing:
                raise ValueError(f"record {i}: missing required fields: {', '.join(missing)}")
            rows.append(row)
        return pd.DataFrame(rows, columns=self.features)

    def _reasons(self, row: pd.Series, top: int = 3) -> list[dict]:
        """Which of this customer's values stand out vs all customers (Thai + English text)."""
        found = []
        for col, (label, label_en) in REASON_LABELS.items():
            val = row.get(col)
            if val is None or pd.isna(val):
                continue
            q = np.asarray(self.meta["percentiles"][col])
            pct = (np.searchsorted(q, val, "left") + np.searchsorted(q, val, "right")) / 2 / len(q) * 100
            if abs(pct - 50) < 25:
                continue
            if pct > 50:
                share = max(5, int(round((100 - pct) / 5) * 5))
                found.append((abs(pct - 50), {
                    "text": f"{label}สูง (อยู่ใน {share}% แรกของลูกค้า)",
                    "text_en": f"{label_en}: high (top {share}% of customers)",
                    "dir": "up",
                }))
            else:
                share = max(5, int(round(pct / 5) * 5))
                found.append((abs(pct - 50), {
                    "text": f"{label}ต่ำ (อยู่ใน {share}% ล่างสุดของลูกค้า)",
                    "text_en": f"{label_en}: low (bottom {share}% of customers)",
                    "dir": "down",
                }))
        return [r for _, r in sorted(found, key=lambda x: -x[0])[:top]]

    def predict(self, records: list[dict], fill_missing: bool = False) -> list[dict]:
        df = self._to_frame(records, fill_missing)
        Xt = self.pipeline[:-1].transform(df)
        dist = self.pipeline.named_steps["model"].transform(Xt)  # distance to every centroid
        order = np.argsort(dist, axis=1)
        rows = np.arange(len(df))
        d1, d2 = dist[rows, order[:, 0]], dist[rows, order[:, 1]]
        # 0 = sitting on the boundary between two segments, ->1 = clearly inside one
        confidence = np.where(d2 > 0, 1 - d1 / d2, 1.0)

        results = []
        for i in range(len(df)):
            seg = self.meta["segments"][str(int(order[i, 0]))]
            runner_up = self.meta["segments"][str(int(order[i, 1]))]
            results.append(
                {
                    "cluster": int(order[i, 0]),
                    "segment": seg["name"],
                    "segment_th": seg["name_th"],
                    "description_th": seg["description_th"],
                    "description_en": seg["description_en"],
                    "strategy": seg["strategy"],
                    "strategy_th": seg["strategy_th"],
                    "confidence": round(float(confidence[i]), 3),
                    "second_best_segment": runner_up["name"],
                    "second_best_segment_th": runner_up["name_th"],
                    "reasons": self._reasons(df.iloc[i]),
                }
            )
        return results
