import streamlit as st
import pickle
import pandas as pd
import requests
import random
import altair as alt

# Page Configuration
st.set_page_config(
    page_title="CineMatch | AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Cinematic UI / UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Gradient Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(15, 16, 35, 0.95) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(129, 140, 248, 0.4);
        color: #a5b4fc;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 0;
        line-height: 1.6;
    }

    /* Spotlight Card for Selected Movie */
    .spotlight-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }

    /* Badges */
    .meta-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 6px 0 10px 0;
    }
    .badge-rating {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #000000 !important;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        display: inline-flex;
        align-items: center;
    }
    .badge-year {
        background: #334155;
        color: #e2e8f0 !important;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
    }
    .badge-match {
        background: linear-gradient(135deg, #10b981, #059669);
        color: #ffffff !important;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
    }
    .badge-genre {
        background: rgba(99, 102, 241, 0.2);
        color: #c7d2fe !important;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 500;
    }

    /* Movie Poster Styling */
    div[data-testid="stImage"] img {
        border-radius: 12px;
        transition: transform 0.28s ease, box-shadow 0.28s ease;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
        object-fit: cover;
        width: 100%;
    }
    div[data-testid="stImage"] img:hover {
        transform: translateY(-5px) scale(1.025);
        box-shadow: 0 14px 28px rgba(99, 102, 241, 0.35);
    }

    /* Sidebar info box */
    .sidebar-info {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: #94a3b8;
    }

    /* Button Primary Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)


# Load Data
@st.cache_resource
def load_data():
    movies = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()
movie_titles = list(movies['title'].values)


# Fetch Movie Details & Poster with Caching
@st.cache_data(show_spinner=False)
def get_movie_details(title, movie_id=None):
    # Try fetching details and high-res poster from OMDb API
    try:
        url = "https://www.omdbapi.com/"
        response = requests.get(url, params={"t": title, "apikey": "trilogy"}, timeout=4)
        data = response.json()
        if data.get("Response") == "True":
            poster = data.get("Poster")
            if not poster or poster == "N/A":
                poster = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=60"
            return {
                "title": data.get("Title", title),
                "year": data.get("Year", "N/A"),
                "genre": data.get("Genre", "Film"),
                "rating": data.get("imdbRating", "N/A"),
                "plot": data.get("Plot", "No plot overview available."),
                "director": data.get("Director", "N/A"),
                "actors": data.get("Actors", "N/A"),
                "poster": poster
            }
    except Exception:
        pass

    # Fallback to TMDB API if available
    if movie_id:
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265ac1679637bc7ff91008432f55e37&language=en-US"
            data = requests.get(url, timeout=2).json()
            poster_path = data.get("poster_path")
            if poster_path:
                return {
                    "title": data.get("title", title),
                    "year": str(data.get("release_date", ""))[:4] or "N/A",
                    "genre": ", ".join([g["name"] for g in data.get("genres", [])]) or "Film",
                    "rating": str(round(data.get("vote_average", 0), 1)) or "N/A",
                    "plot": data.get("overview", "No plot overview available."),
                    "director": "N/A",
                    "actors": "N/A",
                    "poster": "https://image.tmdb.org/t/p/w500/" + poster_path
                }
        except Exception:
            pass

    # Fallback placeholder if no API returns data
    return {
        "title": title,
        "year": "N/A",
        "genre": "Film",
        "rating": "N/A",
        "plot": "Explore recommendations below based on content and keyword similarities.",
        "director": "N/A",
        "actors": "N/A",
        "poster": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=60"
    }


# Recommendation Engine
def recommend(movie, top_n=5):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:top_n + 1]

    recommendations = []
    for i in movies_list:
        idx = i[0]
        score = i[1]
        m_id = movies.iloc[idx]['movie_id']
        m_title = movies.iloc[idx]['title']
        details = get_movie_details(m_title, m_id)
        details['similarity_score'] = score
        details['match_percent'] = round(score * 100, 1)
        recommendations.append(details)

    return recommendations


# Session State Management
if "current_movie" not in st.session_state:
    st.session_state.current_movie = "Avatar"
if "last_recommended_for" not in st.session_state:
    st.session_state.last_recommended_for = None
if "cached_recommendations" not in st.session_state:
    st.session_state.cached_recommendations = None


# Sidebar Controls
with st.sidebar:
    st.markdown("### 🎬 CineMatch Hub")
    st.caption("AI-Powered Content-Based Recommender")
    st.divider()

    st.markdown("#### ⚙️ Settings")
    top_n = st.slider("Number of Recommendations:", min_value=4, max_value=10, value=5, step=1)

    st.markdown("#### 🎲 Feeling Adventurous?")
    if st.button("Surprise Me!", use_container_width=True, type="secondary"):
        st.session_state.current_movie = random.choice(movie_titles)
        st.session_state.cached_recommendations = None
        st.rerun()

    st.divider()
    st.markdown("#### 📊 Dataset Metrics")
    c1, c2 = st.columns(2)
    c1.metric("Indexed Movies", f"{len(movies):,}")
    c2.metric("Features", "5,000")

    st.markdown("""
    <div class="sidebar-info">
        <b>Engine:</b> Cosine Similarity over Bag-of-Words vectors.<br>
        <b>Metadata:</b> Cast, Director, Genres, Keywords & Plot Tags.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("[🔗 GitHub Repository](https://github.com/Aniketsingh-45/movie_recommanding_system)")


# Hero Section
st.markdown("""
<div class="hero-container">
    <span class="hero-badge">✨ Machine Learning Discovery</span>
    <h1 class="hero-title">Discover Movies You'll Love</h1>
    <p class="hero-subtitle">
        Intelligent content-based recommendations powered by NLP, CountVectorizer, and Cosine Distance.
        Select your favorite movie below to find similar titles.
    </p>
</div>
""", unsafe_allow_html=True)


# Main Search & Interactive Selector
col_search, col_btn = st.columns([4, 1], gap="medium")

# Determine default selectbox index safely
current_index = 0
if st.session_state.current_movie in movie_titles:
    current_index = movie_titles.index(st.session_state.current_movie)

with col_search:
    selected_movie = st.selectbox(
        "Search or pick a movie:",
        options=movie_titles,
        index=current_index,
        help="Type to search among 4,800+ movies"
    )
    if selected_movie != st.session_state.current_movie:
        st.session_state.current_movie = selected_movie
        st.session_state.cached_recommendations = None

with col_btn:
    st.write("")
    st.write("")
    recommend_clicked = st.button("Get Recommendations 🚀", type="primary", use_container_width=True)


# Interactive Spotlight Card for Selected Movie
selected_details = get_movie_details(st.session_state.current_movie)

with st.container():
    st.markdown("#### 🎯 Currently Selected Movie")
    spot_col1, spot_col2 = st.columns([1, 4], gap="large")
    with spot_col1:
        st.image(selected_details["poster"], use_container_width=True)
    with spot_col2:
        st.markdown(f"### {selected_details['title']}")
        st.markdown(
            f"<div class='meta-badges'>"
            f"<span class='badge-rating'>⭐ {selected_details['rating']} / 10</span> "
            f"<span class='badge-year'>📅 {selected_details['year']}</span> "
            f"<span class='badge-genre'>🏷️ {selected_details['genre']}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown(f"**Director:** {selected_details['director']} | **Cast:** {selected_details['actors']}")
        st.write(selected_details['plot'])

st.divider()


# Perform Recommendation on Click or Load from Cache
if recommend_clicked or (st.session_state.cached_recommendations is not None and st.session_state.last_recommended_for == st.session_state.current_movie):
    if recommend_clicked:
        with st.spinner("Analyzing similarity vectors and gathering posters..."):
            recommendations = recommend(st.session_state.current_movie, top_n=top_n)
            st.session_state.cached_recommendations = recommendations
            st.session_state.last_recommended_for = st.session_state.current_movie
    else:
        recommendations = st.session_state.cached_recommendations

    # Navigation Tabs
    tab_rec, tab_analytics, tab_engine = st.tabs([
        "🍿 Recommended Movies",
        "📊 Similarity Analytics",
        "🧠 How the Engine Works"
    ])

    # Tab 1: Visual Recommendations Grid
    with tab_rec:
        st.markdown(f"### Movies Similar to *{st.session_state.current_movie}*")
        
        # Display in rows of 5 cards
        cols_per_row = 5
        for row_start in range(0, len(recommendations), cols_per_row):
            batch = recommendations[row_start:row_start + cols_per_row]
            cols = st.columns(len(batch), gap="medium")
            for col, item in zip(cols, batch):
                with col:
                    st.image(item["poster"], use_container_width=True)
                    st.markdown(f"**{item['title']}**")
                    st.markdown(
                        f"<div class='meta-badges'>"
                        f"<span class='badge-rating'>⭐ {item['rating']}</span> "
                        f"<span class='badge-year'>{item['year']}</span> "
                        f"<span class='badge-match'>🎯 {item['match_percent']}%</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    with st.expander("📖 Synopsis"):
                        st.markdown(f"**Genre:** {item['genre']}")
                        st.markdown(f"**Director:** {item['director']}")
                        st.caption(item['plot'])

    # Tab 2: Similarity Analytics
    with tab_analytics:
        st.markdown("### 📊 Similarity Match Comparison")
        st.caption(f"Cosine similarity scores measured against **{st.session_state.current_movie}**")

        chart_df = pd.DataFrame({
            "Movie": [m["title"] for m in recommendations],
            "Match Percentage (%)": [m["match_percent"] for m in recommendations],
            "IMDb Rating": [float(m["rating"]) if m["rating"] != "N/A" else 0.0 for m in recommendations]
        })

        chart = alt.Chart(chart_df).mark_bar(
            cornerRadiusTopRight=8,
            cornerRadiusBottomRight=8,
            height=28
        ).encode(
            x=alt.X("Match Percentage (%):Q", title="Cosine Similarity Score (%)", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Movie:N", sort="-x", title=""),
            color=alt.Color("Match Percentage (%):Q", scale=alt.Scale(scheme="plasma"), legend=None),
            tooltip=["Movie", "Match Percentage (%)", "IMDb Rating"]
        ).properties(height=350)

        st.altair_chart(chart, use_container_width=True)

        m_col1, m_col2, m_col3 = st.columns(3)
        top_match = recommendations[0]
        avg_match = round(sum([m["match_percent"] for m in recommendations]) / len(recommendations), 1)
        m_col1.metric("Highest Similarity Match", f"{top_match['title']}", f"{top_match['match_percent']}%")
        m_col2.metric("Average Recommendation Match", f"{avg_match}%")
        m_col3.metric("Total Recommendations", f"{len(recommendations)}")

    # Tab 3: Engine Deep Dive
    with tab_engine:
        st.markdown("### 🧠 How Content-Based Filtering Works")
        st.markdown("""
        This recommendation engine computes similarities using **natural language processing (NLP)** and **vector space modeling**:
        
        1. **Feature Extraction**:
           - Merged metadata fields: `overview`, `genres`, `keywords`, top 3 `cast` members, and the `director`.
           - Entities with multiple words (e.g. *James Cameron* $\\rightarrow$ *jamescameron*) were joined to avoid false overlap with other entities sharing common names.
        
        2. **Text Normalization & Stemming**:
           - Applied **PorterStemmer** from NLTK to reduce words to their root forms (e.g. *activities*, *activity* $\\rightarrow$ *activ*).
        
        3. **Vectorization**:
           - Extracted the **5,000 most frequent words** using Scikit-Learn's `CountVectorizer(stop_words='english')`.
           - Formed a $4,806 \\times 5,000$ sparse feature matrix.
        
        4. **Cosine Similarity Metric**:
           - Computed angular distance between movie vectors:
        """)
        st.latex(r"\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\| \|v\|}")
        st.info("The closer the cosine value is to 1, the more similar the themes, crew, and narrative tags between the movies.")

else:
    st.info("👆 Click **'Get Recommendations 🚀'** above to explore similar movies!")