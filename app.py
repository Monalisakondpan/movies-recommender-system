import pickle

import pandas as pd
import requests
import streamlit as st

API_KEY = st.secrets["TMDB_API_KEY"]
FALLBACK_POSTER = "https://placehold.co/500x750?text=No+Poster"


@st.cache_resource
def load_data():
    movies = pd.DataFrame(pickle.load(open("movie_dict.pkl", "rb")))
    top5 = pickle.load(open("top5.pkl", "rb"))
    return movies, top5


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


def recommend(movie, movies, top5):
    idx = movies[movies["title"] == movie].index[0]
    id_col = "movie_id" if "movie_id" in movies.columns else "id"
    names, posters = [], []
    for i in top5[idx]:
        row = movies.iloc[int(i)]
        names.append(row["title"])
        posters.append(fetch_poster(row[id_col]))
    return names, posters


movies, top5 = load_data()

st.title("Movie Recommender System")
selected_movie = st.selectbox("Select a movie to get recommendations:", movies["title"].values)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie, movies, top5)

    for col, name, poster in zip(st.columns(len(names)), names, posters):
        with col:
            st.image(poster)
            st.markdown(f"**{name}**")