import pandas as pd
import numpy as np


def detect_anomalies(df, z_threshold=2.0, min_months=3):
    """
    Detects statistically unusual crime spikes per district per month.

    Method: for each district, compute the monthly FIR count, then
    z-score each month against that district's own historical mean/std.
    A month is flagged as an anomaly if its z-score exceeds z_threshold,
    meaning the spike is genuinely unusual for that specific district
    (not just compared to other districts).

    Returns a list of anomaly dicts sorted by severity (highest z-score first).
    """
    work = df.copy()
    work["fir_date"] = pd.to_datetime(work["fir_date"], errors="coerce")
    work["year_month"] = work["fir_date"].dt.to_period("M").astype(str)

    monthly = (
        work.groupby(["district", "year_month"])
        .size()
        .reset_index(name="crime_count")
    )

    anomalies = []

    for district, grp in monthly.groupby("district"):
        grp = grp.sort_values("year_month")
        if len(grp) < min_months:
            continue

        mean = grp["crime_count"].mean()
        std = grp["crime_count"].std()
        if std == 0 or pd.isna(std):
            continue

        grp = grp.copy()
        grp["z_score"] = (grp["crime_count"] - mean) / std

        spikes = grp[grp["z_score"] >= z_threshold]
        for _, row in spikes.iterrows():
            month_data = work[
                (work["district"] == district)
                & (work["year_month"] == row["year_month"])
            ]
            top_crime = (
                month_data["crime_type"].value_counts().idxmax()
                if len(month_data) > 0
                else "Unknown"
            )

            anomalies.append({
                "district":      district,
                "month":         row["year_month"],
                "crime_count":   int(row["crime_count"]),
                "historical_avg": round(mean, 1),
                "z_score":       round(row["z_score"], 2),
                "pct_above_avg": round(((row["crime_count"] - mean) / mean) * 100, 1),
                "top_crime_type": top_crime,
                "severity": "Critical" if row["z_score"] >= 3.0 else "Elevated",
            })

    anomalies.sort(key=lambda x: x["z_score"], reverse=True)
    return anomalies


def get_anomaly_summary(anomalies):
    if not anomalies:
        return {"total": 0, "critical": 0, "districts_affected": 0}
    return {
        "total": len(anomalies),
        "critical": sum(1 for a in anomalies if a["severity"] == "Critical"),
        "districts_affected": len(set(a["district"] for a in anomalies)),
    }


if __name__ == "__main__":
    df = pd.read_csv("../data/karnataka_fir_synthetic.csv")
    anomalies = detect_anomalies(df)
    print(f"Found {len(anomalies)} anomalies")
    for a in anomalies[:10]:
        print(f"  {a['district']} ({a['month']}): {a['crime_count']} crimes "
              f"vs avg {a['historical_avg']} — z={a['z_score']} [{a['severity']}]")