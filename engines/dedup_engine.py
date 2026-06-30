import pandas as pd
from difflib import SequenceMatcher
import re

WEIGHTS = {"phone_last4": 0.35, "name": 0.30, "age": 0.20, "district": 0.15}

NEIGHBORING_DISTRICTS = {
    "Bengaluru Urban":  ["Tumakuru", "Hassan"],
    "Mysuru":           ["Hassan", "Chamarajanagar"],
    "Mangaluru":        ["Udupi"],
    "Hubballi-Dharwad": ["Gadag", "Haveri", "Belagavi"],
    "Belagavi":         ["Bagalkot", "Vijayapura"],
    "Kalaburagi":       ["Bidar", "Raichur"],
    "Ballari":          ["Raichur", "Davangere"],
}

def score_name(n1, n2):
    a = str(n1).lower().strip()
    b = str(n2).lower().strip()
    return SequenceMatcher(None, a, b).ratio()

def score_age(a1, a2):
    d = abs(int(a1) - int(a2))
    return 1.0 if d == 0 else 0.67 if d <= 2 else 0.33 if d <= 3 else 0.0

def score_phone(p1, p2):
    return 1.0 if str(p1)[-4:] == str(p2)[-4:] else 0.0

def score_district(d1, d2):
    if d1 == d2: return 1.0
    return 0.5 if d2 in NEIGHBORING_DISTRICTS.get(d1, []) else 0.0

def compute_confidence(r1, r2):
    s = (WEIGHTS["name"]        * score_name(r1["accused_name"],   r2["accused_name"]) +
         WEIGHTS["age"]         * score_age(r1["accused_age"],     r2["accused_age"])  +
         WEIGHTS["phone_last4"] * score_phone(r1["accused_phone"], r2["accused_phone"])+
         WEIGHTS["district"]    * score_district(r1["district"],   r2["district"]))
    return round(s * 100, 1)

def soundex_simple(name):
    name = re.sub(r'[^a-zA-Z]', '', str(name).split()[0]).upper()
    if not name: return "Z000"
    codes = {'BFPV':'1','CGJKQSXYZ':'2','DT':'3','L':'4','MN':'5','R':'6'}
    result = name[0]
    for ch in name[1:]:
        for key, code in codes.items():
            if ch in key:
                if code != (result[-1] if len(result) > 1 else ''):
                    result += code
                break
    return (result + "000")[:4]

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py: self.parent[px] = py

def run_dedup(df, threshold=60.0):
    suspects = df[["fir_id","accused_name","accused_age",
                   "accused_phone","district"]].reset_index(drop=True)
    n = len(suspects)
    print(f"Running dedup on {n} suspects...")

    uf = UnionFind(n)
    blocks = {}
    for i, row in suspects.iterrows():
        key = soundex_simple(row["accused_name"])
        blocks.setdefault(key, []).append(i)

    matches = 0
    for idxs in blocks.values():
        for i in range(len(idxs)):
            for j in range(i+1, len(idxs)):
                conf = compute_confidence(suspects.iloc[idxs[i]], suspects.iloc[idxs[j]])
                if conf >= threshold:
                    uf.union(idxs[i], idxs[j])
                    matches += 1

    print(f"Matches found: {matches}")
    cmap = {}; cc = 0; cids = []
    for i in range(n):
        r = uf.find(i)
        if r not in cmap: cmap[r] = f"CLUSTER_{cc:04d}"; cc += 1
        cids.append(cmap[r])

    suspects["cluster_id"] = cids
    sizes = suspects["cluster_id"].value_counts()
    suspects["cluster_size"] = suspects["cluster_id"].map(sizes)

    dups = suspects[suspects["cluster_size"] > 1]
    print(f"Identity clusters found: {dups['cluster_id'].nunique()}")
    print(f"Total alias records grouped: {len(dups)}")

    result = df.copy()
    result["cluster_id"]   = suspects["cluster_id"].values
    result["cluster_size"] = suspects["cluster_size"].values
    return result

def get_identity_clusters(df_deduped):
    clusters = []
    multi = df_deduped[df_deduped["cluster_size"] > 1]
    for cid, grp in multi.groupby("cluster_id"):
        conf = compute_confidence(grp.iloc[0], grp.iloc[1]) if len(grp) >= 2 else 0
        clusters.append({
            "cluster_id":  cid,
            "alias_count": len(grp),
            "confidence":  conf,
            "names_found": list(grp["accused_name"].unique()),
            "districts":   list(grp["district"].unique()),
            "records":     grp[["fir_id","accused_name","accused_age",
                                 "accused_phone","district","crime_type",
                                 "fir_date","cluster_size"]].to_dict("records"),
        })
    clusters.sort(key=lambda x: x["alias_count"], reverse=True)
    return clusters

def search_suspect(df_deduped, query_name):
    results = []
    for _, row in df_deduped.iterrows():
        sim = score_name(query_name, row["accused_name"])
        if sim > 0.65:
            results.append({
                "fir_id":       row["fir_id"],
                "name":         row["accused_name"],
                "age":          row["accused_age"],
                "district":     row["district"],
                "crime_type":   row["crime_type"],
                "cluster_id":   row["cluster_id"],
                "cluster_size": int(row["cluster_size"]),
                "name_similarity": round(sim * 100, 1),
            })
    results.sort(key=lambda x: x["name_similarity"], reverse=True)
    return results[:20]

if __name__ == "__main__":
    df = pd.read_csv("../data/karnataka_fir_synthetic.csv")
    df_d = run_dedup(df, threshold=60.0)
    clusters = get_identity_clusters(df_d)
    print(f"\nTop clusters found:")
    for c in clusters[:5]:
        print(f"\n  Cluster: {c['cluster_id']}")
        print(f"  Names:   {c['names_found']}")
        print(f"  Districts: {c['districts']}")
        print(f"  Aliases: {c['alias_count']}  Confidence: {c['confidence']}%")