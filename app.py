import pickle

import pandas as pd
import requests
import streamlit as st

API_KEY = st.secrets["TMDB_API_KEY"]
FALLBACK_POSTER = "https://placehold.co/500x750?text=No+Poster"


def make_label(row):
    if pd.notna(row["year"]):
        return f"{row['title']} ({int(row['year'])})"
    return row["title"]


@st.cache_resource
def load_data():
    movies = pd.DataFrame(pickle.load(open("movie_dict.pkl", "rb")))
    movies["label"] = movies.apply(make_label, axis=1)
    top5 = pickle.load(open("top5.pkl", "rb"))
    meta = pickle.load(open("meta.pkl", "rb"))

    label_to_idx = {}
    for i, lab in enumerate(movies["label"]):
        label_to_idx.setdefault(lab, i)
    labels = sorted(label_to_idx, key=str.lower)

    return movies, top5, meta, label_to_idx, labels


@st.cache_data(show_spinner=False)
def _get_poster_path(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    r = requests.get(url, params={"api_key": API_KEY, "language": "en-US"}, timeout=10)
    r.raise_for_status()
    return r.json().get("poster_path")


def fetch_poster(movie_id):
    try:
        path = _get_poster_path(int(movie_id))
        if path:
            return "https://image.tmdb.org/t/p/w500" + path
    except requests.RequestException as e:
        print(f"[poster] movie_id={movie_id} failed: {e}")
    return FALLBACK_POSTER


def explain(src_id, rec_id, meta):
    a, b = meta.get(int(src_id)), meta.get(int(rec_id))
    if not a or not b:
        return ""
    parts = []
    for key, label, limit in [
        ("director", "Director", 1),
        ("cast", "Cast", 2),
        ("genres", "Genre", 3),
        ("keywords", "Theme", 3),
    ]:
        src_set = set(a[key])
        shared = [x for x in b[key] if x in src_set][:limit]
        if shared:
            parts.append(f"{label}: {', '.join(shared)}")
    return " · ".join(parts) if parts else "Similar plot description"


def recommend(idx, movies, top5, meta):
    src_id = movies.iloc[idx]["movie_id"]
    results = []
    for i in top5[idx]:
        row = movies.iloc[int(i)]
        results.append({
            "name": row["label"],
            "poster": fetch_poster(row["movie_id"]),
            "reason": explain(src_id, row["movie_id"], meta),
        })
    return results


movies, top5, meta, label_to_idx, labels = load_data()

st.title("Movie Recommender System")
st.caption(f"{len(labels):,} movies · type in the box to search")

selected = st.selectbox("Select a movie to get recommendations:", labels)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        results = recommend(label_to_idx[selected], movies, top5, meta)

    for col, r in zip(st.columns(len(results)), results):
        with col:
            st.image(r["poster"])
            st.markdown(f"**{r['name']}**")
            if r["reason"]:
                st.caption(r["reason"])