import pandas as pd
import numpy as np


# How dangerous each crime type is treated, on a 1 (least) - 10 (most) scale.
# Used to weight a district's crime MIX, not just its raw volume.
CRIME_SEVERITY = {
    "Murder":              10,
    "Attempt to Murder":   9,
    "Dacoity":             8,
    "Kidnapping":          7,
    "Robbery":             6,
    "Chain Snatching":     5,
    "Burglary":            5,
    "Vehicle Theft":       4,
    "Assault":             4,
    "Cheating/Fraud":      3,
    "Theft":               2,
}

# Weight of each factor in the final 0-100 risk score.
# These are intentionally simple and explainable, not a black-box model -
# a judge (or an officer) can see exactly why a district scored the way it did.
WEIGHTS = {
    "trend":      0.35,   # is crime rising or falling recently?
    "severity":   0.25,   # how violent is the crime mix?
    "anomaly":    0.20,   # history of statistical spikes (from anomaly_detector)
    "backlog":    0.20,   # % of cases still unresolved
}

TREND_MONTHS = 6  # how many recent months to look at for the trend line


def _monthly_counts(df):
    work = df.copy()
    work["fir_date"] = pd.to_datetime(work["fir_date"], errors="coerce")
    work["year_month"] = work["fir_date"].dt.to_period("M").astype(str)
    return work


def _trend_slope_and_forecast(district_work):
    """
    Fits a straight line through the district's last TREND_MONTHS of
    monthly FIR counts. Returns (slope, predicted_next_month_count).
    A positive slope means crime is climbing month over month.
    """
    monthly = (
        district_work.groupby("year_month")
        .size()
        .reset_index(name="count")
        .sort_values("year_month")
    )
    recent = monthly.tail(TREND_MONTHS)

    if len(recent) < 3:
        last_count = recent["count"].iloc[-1] if len(recent) else 0
        return 0.0, int(last_count)

    x = np.arange(len(recent))
    y = recent["count"].values
    slope, intercept = np.polyfit(x, y, 1)

    predicted_next = max(0, round(slope * len(recent) + intercept))
    return float(slope), int(predicted_next)


def _severity_score(district_work):
    """Average severity (1-10) of crimes in this district, recent months weighted more."""
    counts = district_work["crime_type"].value_counts()
    total = counts.sum()
    if total == 0:
        return 0.0
    weighted = sum(CRIME_SEVERITY.get(ct, 3) * n for ct, n in counts.items())
    return weighted / total


def _backlog_ratio(district_work):
    unresolved = district_work["case_status"].isin(["Open", "Under Investigation"]).sum()
    total = len(district_work)
    return unresolved / total if total else 0.0


def compute_risk_scores(df, anomalies=None):
    """
    Computes a 0-100 predictive risk score per district from four
    explainable signals: recent trend, crime severity mix, anomaly
    history, and unresolved-case backlog.

    Returns a list of dicts sorted by risk_score descending, each with
    a breakdown so the score is auditable rather than a black box.
    """
    anomalies = anomalies or []
    anomaly_counts = {}
    for a in anomalies:
        anomaly_counts[a["district"]] = anomaly_counts.get(a["district"], 0) + 1
    max_anomalies = max(anomaly_counts.values()) if anomaly_counts else 1

    work = _monthly_counts(df)
    districts = sorted(work["district"].unique().tolist())

    raw = []
    for district in districts:
        d_work = work[work["district"] == district]

        slope, predicted_next = _trend_slope_and_forecast(d_work)
        severity = _severity_score(d_work)
        anomaly_n = anomaly_counts.get(district, 0)
        backlog = _backlog_ratio(d_work)

        last_month_count = (
            d_work.groupby("year_month").size().sort_index().iloc[-1]
            if len(d_work) else 0
        )

        raw.append({
            "district": district,
            "slope": slope,
            "predicted_next_month": predicted_next,
            "last_month_count": int(last_month_count),
            "severity": severity,
            "anomaly_n": anomaly_n,
            "backlog": backlog,
            "total_crimes": len(d_work),
        })

    # Normalize trend slope and severity across districts to 0-1 so they
    # combine fairly with anomaly count and backlog ratio (already 0-1-ish).
    slopes = [r["slope"] for r in raw]
    min_slope, max_slope = min(slopes), max(slopes)
    slope_range = (max_slope - min_slope) or 1.0

    severities = [r["severity"] for r in raw]
    min_sev, max_sev = min(severities), max(severities)
    sev_range = (max_sev - min_sev) or 1.0

    results = []
    for r in raw:
        trend_norm = (r["slope"] - min_slope) / slope_range
        severity_norm = (r["severity"] - min_sev) / sev_range
        anomaly_norm = r["anomaly_n"] / max_anomalies
        backlog_norm = r["backlog"]  # already 0-1

        score = 100 * (
            WEIGHTS["trend"] * trend_norm +
            WEIGHTS["severity"] * severity_norm +
            WEIGHTS["anomaly"] * anomaly_norm +
            WEIGHTS["backlog"] * backlog_norm
        )
        score = round(min(100, max(0, score)), 1)

        if score >= 70:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 30:
            level = "Medium"
        else:
            level = "Low"

        results.append({
            "district": r["district"],
            "risk_score": score,
            "risk_level": level,
            "predicted_next_month": r["predicted_next_month"],
            "last_month_count": r["last_month_count"],
            "trend_direction": "Rising" if r["slope"] > 0.15 else ("Falling" if r["slope"] < -0.15 else "Stable"),
            "severity_index": round(r["severity"], 1),
            "anomaly_count": r["anomaly_n"],
            "backlog_pct": round(r["backlog"] * 100, 1),
            "total_crimes": r["total_crimes"],
            "breakdown": {
                "trend_contribution":    round(WEIGHTS["trend"] * trend_norm * 100, 1),
                "severity_contribution": round(WEIGHTS["severity"] * severity_norm * 100, 1),
                "anomaly_contribution":  round(WEIGHTS["anomaly"] * anomaly_norm * 100, 1),
                "backlog_contribution":  round(WEIGHTS["backlog"] * backlog_norm * 100, 1),
            },
        })

    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results


def get_risk_summary(results):
    if not results:
        return {"critical": 0, "high": 0, "medium": 0, "low": 0, "top_district": None}
    return {
        "critical": sum(1 for r in results if r["risk_level"] == "Critical"),
        "high":     sum(1 for r in results if r["risk_level"] == "High"),
        "medium":   sum(1 for r in results if r["risk_level"] == "Medium"),
        "low":      sum(1 for r in results if r["risk_level"] == "Low"),
        "top_district": results[0]["district"],
    }


if __name__ == "__main__":
    df = pd.read_csv("../data/karnataka_fir_synthetic.csv")
    from anomaly_detector import detect_anomalies
    anomalies = detect_anomalies(df)
    scores = compute_risk_scores(df, anomalies)
    print(f"{'District':<20}{'Score':<8}{'Level':<10}{'Trend':<10}{'Predicted Next Mo.'}")
    for r in scores:
        print(f"{r['district']:<20}{r['risk_score']:<8}{r['risk_level']:<10}{r['trend_direction']:<10}{r['predicted_next_month']}")
