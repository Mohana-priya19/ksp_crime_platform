import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_mo_index(df):
    def row_to_text(row):
        parts = [
            str(row.get("crime_type", "")),
            str(row.get("district", "")),
            str(row.get("location_type", "")),
            str(row.get("weapon_used", "")),
            str(row.get("fir_time", "")).split(":")[0] + "h",
            "victim_age_" + str(int(row.get("victim_age", 0)) // 10 * 10),
        ]
        return " ".join(parts).lower()

    texts = df.apply(row_to_text, axis=1).tolist()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def search_similar_cases(query_text, vectorizer, matrix, df, top_n=5):
    query_vec = vectorizer.transform([query_text.lower()])
    scores = cosine_similarity(query_vec, matrix).flatten()
    top_indices = scores.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        row = df.iloc[idx]
        results.append({
            "fir_id":        row["fir_id"],
            "similarity":    round(float(scores[idx]) * 100, 1),
            "crime_type":    row["crime_type"],
            "district":      row["district"],
            "location_type": row["location_type"],
            "weapon_used":   row["weapon_used"],
            "fir_date":      row["fir_date"],
            "fir_time":      row["fir_time"],
            "accused_name":  row["accused_name"],
            "victim_age":    int(row["victim_age"]),
            "case_status":   row["case_status"],
        })
    return results