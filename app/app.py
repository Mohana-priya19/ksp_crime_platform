import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, jsonify, request
import pandas as pd
import json

from engines.data_generator import generate_fir_records
from engines.dedup_engine import run_dedup, get_identity_clusters, search_suspect

app = Flask(__name__, static_folder="static")

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/karnataka_fir_synthetic.csv")

def load_data():
    if os.path.exists(DATA_PATH):
        print("Loading existing dataset...")
        df = pd.read_csv(DATA_PATH)
    else:
        print("Generating dataset...")
        df = generate_fir_records(5000)
        df.to_csv(DATA_PATH, index=False)
    return df

print("Starting platform...")
df_raw     = load_data()
df_deduped = run_dedup(df_raw, threshold=60.0)
clusters   = get_identity_clusters(df_deduped)
clusters_by_id = {c["cluster_id"]: c for c in clusters}
print(f"Ready. {len(df_raw)} records. {len(clusters)} clusters found.")

@app.route("/")
def index():
    stats = {
        "total_crimes":      len(df_raw),
        "open_cases":        int((df_raw["case_status"] == "Open").sum()),
        "districts":         df_raw["district"].nunique(),
        "identity_clusters": len(clusters),
        "aliases_caught":    sum(c["alias_count"] for c in clusters),
    }
    return render_template("index.html", stats=stats)

@app.route("/dedup")
def dedup_page():
    return render_template("dedup.html", clusters=clusters[:20],
                           total_clusters=len(clusters))

@app.route("/suspect/<cluster_id>")
def suspect_profile(cluster_id):
    cluster = clusters_by_id.get(cluster_id)
    if not cluster:
        return "Suspect cluster not found", 404
    return render_template("suspect.html", cluster=cluster)

@app.route("/network")
def network_page():
    nodes = []
    links = []
    district_node_ids = set()
    district_cluster_count = {}

    top_clusters = clusters[:30]

    for c in top_clusters:
        cluster_node_id = f"cluster_{c['cluster_id']}"
        nodes.append({
            "id": cluster_node_id,
            "type": "cluster",
            "label": c["names_found"][0],
            "names": ", ".join(c["names_found"]),
            "alias_count": c["alias_count"],
            "confidence": c["confidence"],
            "cluster_id": c["cluster_id"],
            "r": min(22, 6 + c["alias_count"] * 2.5),
        })
        for d in c["districts"]:
            district_id = f"district_{d}"
            if district_id not in district_node_ids:
                district_node_ids.add(district_id)
                nodes.append({
                    "id": district_id,
                    "type": "district",
                    "label": d,
                    "r": 10,
                })
            district_cluster_count[district_id] = district_cluster_count.get(district_id, 0) + 1
            links.append({
                "source": cluster_node_id,
                "target": district_id,
                "type": "cluster-district",
            })

    for n in nodes:
        if n["type"] == "district":
            n["cluster_count"] = district_cluster_count.get(n["id"], 0)
            n["r"] = min(26, 8 + n["cluster_count"] * 3)

    graph_json = json.dumps({"nodes": nodes, "links": links})
    return render_template("network.html", graph_json=graph_json)

@app.route("/district")
def district_page():
    selected = request.args.get("district", df_raw["district"].mode()[0])
    district_stats = df_raw.groupby("district").agg(
        total_crimes=("fir_id", "count")
    ).reset_index().sort_values("total_crimes", ascending=False)
    district_stats = district_stats.to_dict("records")

    district_data   = df_raw[df_raw["district"] == selected]
    crime_breakdown = district_data["crime_type"].value_counts().to_dict()
    total           = len(district_data)

    return render_template("district.html",
                           district_stats=district_stats,
                           selected=selected,
                           crime_breakdown=crime_breakdown,
                           total=total)

@app.route("/map")
def map_page():
    crime_type = request.args.get("crime_type", "All")
    crime_types = ["All"] + sorted(df_raw["crime_type"].unique().tolist())

    if crime_type == "All":
        filtered = df_raw
    else:
        filtered = df_raw[df_raw["crime_type"] == crime_type]

    from engines.hotspot_map import generate_map_html
    map_html = generate_map_html(filtered)

    return render_template("map.html",
                           map_html=map_html,
                           crime_types=crime_types,
                           selected=crime_type)

@app.route("/api/search_suspect")
def api_search():
    name = request.args.get("name", "")
    if not name:
        return jsonify({"error": "name required"}), 400
    results = search_suspect(df_deduped, name)
    return jsonify({"results": results, "count": len(results)})

@app.route("/api/stats")
def api_stats():
    return jsonify({
        "total_firs":           len(df_raw),
        "open_cases":           int((df_raw["case_status"] == "Open").sum()),
        "districts_covered":    df_raw["district"].nunique(),
        "identity_clusters":    len(clusters),
        "aliases_unmasked":     sum(c["alias_count"] for c in clusters),
        "crime_type_breakdown": df_raw["crime_type"].value_counts().to_dict(),
    })

@app.route("/api/district_crimes")
def api_district_crimes():
    stats = df_raw.groupby("district").agg(
        total_crimes=("fir_id", "count")
    ).reset_index().sort_values("total_crimes", ascending=False)
    return jsonify(stats.to_dict("records"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)