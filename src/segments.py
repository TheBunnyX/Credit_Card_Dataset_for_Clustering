"""Cluster profiling: turn cluster ids into named business segments."""
import pandas as pd

from src.labels import DESC_EN, SEGMENT_GROUP, SEGMENT_TH, TRAIT_DEFS

PROFILE_COLS = [
    "BALANCE",
    "PURCHASES",
    "ONEOFF_PURCHASES",
    "INSTALLMENTS_PURCHASES",
    "CASH_ADVANCE",
    "CREDIT_LIMIT",
    "PAYMENTS",
    "PURCHASES_FREQUENCY",
    "CASH_ADVANCE_FREQUENCY",
    "PRC_FULL_PAYMENT",
    "TENURE",
]

STRATEGIES = {
    "Cash Advance Users": "Use the card mainly as a cash line, not for shopping. Offer lower cash-advance fees, personal-loan or balance-transfer products, and nudge towards purchases with cashback; monitor credit risk closely.",
    "Big Spenders": "Highest value: premium rewards, cashback on large one-off purchases, credit-limit upgrades and concierge perks. Retention matters more than acquisition.",
    "Full Payers (Transactors)": "Frequent, instalment-friendly and pays in full: reward frequency (points, merchant partnerships) and push 0% instalment plans (travel, appliances, smartphones). Low interest income, so earn on interchange and retention.",
    "Installment Shoppers": "Promote low / 0% instalment programmes with partner merchants (travel, household appliances, electronics) and instalment-conversion offers.",
    "Revolvers": "High balance, cash advances and revolving debt, rarely pays in full: balance-transfer and debt-consolidation offers, auto-pay reminders. High interest income but watch default risk.",
    "Low Payers": "Low payments relative to usage: payment reminders, auto-pay enrolment and early-collection outreach; review credit-limit exposure.",
    "Low Activity": "Near-zero balance and few purchases (new/entry-level users, or holders keeping a zero balance to protect their credit profile): entry-level or starter-card features, waived fees, rewards for on-time payment, sign-up and first-purchase cashback.",
    "Mainstream": "Moderate use, mostly pays only part of the bill: personalised offers based on category spend, cross-sell insurance and savings products, nudge towards instalment plans.",
}


def name_segment(z: pd.Series) -> str:
    """Heuristic rule-based name from z-scores of the cluster means.

    These are a starting point - always review against the profile table.
    """
    # Means of skewed columns are compressed, so thresholds are deliberately modest.
    if z["CASH_ADVANCE"] > 0.8 or (z["CASH_ADVANCE"] > 0.4 and z["PURCHASES_FREQUENCY"] < 0):
        return "Cash Advance Users"
    if z["PURCHASES"] > 1.0 or z["ONEOFF_PURCHASES"] > 1.0:
        return "Big Spenders"
    if z["PRC_FULL_PAYMENT"] > 0.8 and z["PURCHASES_FREQUENCY"] > 0:
        return "Full Payers (Transactors)"
    if z["INSTALLMENTS_PURCHASES"] > 0.3 and z["PURCHASES_FREQUENCY"] > 0.5:
        return "Installment Shoppers"
    if z["PAYMENTS"] < -0.4 and z["BALANCE"] < 0:
        return "Low Payers"
    if z["PURCHASES_FREQUENCY"] < -0.5 and z["PURCHASES"] < 0:
        return "Low Activity"
    if z["BALANCE"] > 0.2 and z["PRC_FULL_PAYMENT"] < 0:
        return "Revolvers"
    return "Mainstream"


def cluster_traits(z: pd.Series, min_abs: float = 0.4, top: int = 4) -> list[dict]:
    """Most distinctive traits of a cluster vs the population, as Thai badges."""
    found = []
    for col, high, low, high_en, low_en in TRAIT_DEFS:
        if abs(z[col]) >= min_abs:
            up = z[col] > 0
            found.append((abs(z[col]), {
                "text": high if up else low,
                "text_en": high_en if up else low_en,
                "dir": "up" if up else "down",
            }))
    return [t for _, t in sorted(found, key=lambda x: -x[0])[:top]]


def profile_clusters(raw: pd.DataFrame, labels) -> dict:
    """Build {cluster_id: {name, size, share, strategy, profile}}."""
    df = raw[PROFILE_COLS].copy()
    df["cluster"] = labels
    means = df.groupby("cluster")[PROFILE_COLS].mean()
    z = (means - df[PROFILE_COLS].mean()) / df[PROFILE_COLS].std()
    sizes = df["cluster"].value_counts()

    names, seen = {}, {}
    for cid in means.index:
        base = name_segment(z.loc[cid])
        seen[base] = seen.get(base, 0) + 1
        names[cid] = base if seen[base] == 1 else f"{base} #{seen[base]}"

    segments = {}
    for cid in means.index:
        base = names[cid].split(" #")[0]
        suffix = names[cid][len(base):]  # "" or " #2"
        name_th, desc_th, strategy_th = SEGMENT_TH[base]
        segments[str(cid)] = {
            "name": names[cid],
            "name_th": name_th + suffix,
            "description_th": desc_th,
            "description_en": DESC_EN[base],
            "group": SEGMENT_GROUP[base],
            "strategy_th": strategy_th,
            "traits": cluster_traits(z.loc[cid]),
            "size": int(sizes[cid]),
            "share": round(float(sizes[cid] / len(df)), 4),
            "strategy": STRATEGIES[base],
            "profile": {c: round(float(means.loc[cid, c]), 3) for c in PROFILE_COLS},
            "zscore": {c: round(float(z.loc[cid, c]), 2) for c in PROFILE_COLS},
        }
    return segments
