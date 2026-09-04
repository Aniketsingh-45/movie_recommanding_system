import streamlit as st
import pickle
import pandas as pd
import requests

st.set_page_config(page_title="Movie Recommender System", layout="wide")


@st.cache_data
def fetch_poster(title, movie_id=None):
    # Fetch poster via OMDb API (fast, reliable, and avoids ISP blocks)
    try:
        url = "https://www.omdbapi.com/"
        response = requests.get(url, params={"t": title, "apikey": "trilogy"}, timeout=4)
        data = response.json()
        poster = data.get("Poster")
        if poster and poster != "N/A":
            return poster
    except Exception:
        pass

    # Fallback to TMDB API if available
    if movie_id:
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265ac1679637bc7ff91008432f55e37&language=en-US"
            data = requests.get(url, timeout=2).json()
            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
        except Exception:
            pass

    # Fallback placeholder image if no poster is found
    return "https://placehold.co/500x750/1e293b/ffffff?text=No+Poster"


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie_names = []
    recommended_movie_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        movie_title = movies.iloc[i[0]]['title']

        recommended_movie_names.append(movie_title)
        recommended_movie_posters.append(fetch_poster(movie_title, movie_id))

    return recommended_movie_names, recommended_movie_posters


movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    'Select or search a movie from the dropdown:',
    movies['title'].values
)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations and posters..."):
        names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])