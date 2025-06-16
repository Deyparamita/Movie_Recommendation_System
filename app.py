import streamlit as st
import pandas as pd

# load data
original_df = pd.read_csv("original_movies.csv")

processed_df = pd.read_csv("processed_movies.csv")                    

# Load precomputed cosine similarity
import joblib
cosine_sim = joblib.load("cosine_sim.pkl")

# Recommend similar movies
def recommend_movies(movie_name, cosine_sim=cosine_sim, df=processed_df, top_n=5):
    idx = df[df['Series_Title'].str.lower() == movie_name.lower()].index

    if len(idx) == 0:
        return []
    idx = idx[0]

    sim_scores = list(enumerate(cosine_sim[idx]))  # sim_scores = (index of movie, similarity score)

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True) # sort based on similarity score in desc order

    sim_scores = sim_scores[1:top_n+1]

    movie_indices = [i[0] for i in sim_scores]

    return df[['Series_Title']].iloc[movie_indices]


# Get full movie details
def get_movie_details(title):
    row = original_df[original_df['Series_Title'].str.lower() == title.lower()]
    if row.empty:
        return None
    row = row.iloc[0]

    overview = row['Overview'] if pd.notna(row['Overview']) else "No overview available"
    posterLink = row['Poster_Link'] if pd.notna(row['Poster_Link']) else "https://via.placeholder.com/300x450?text=No+Image"
    director = row['Director'] if pd.notna(row['Director']) else "Director not available"
    
    return {
        "title": title,
        "overview": overview,
        "director": director,
        "posterLink": posterLink
    }

# streamlit UI
st.title("Movie Recommendation System")

movie_titles = processed_df['Series_Title'].sort_values().tolist()  # Sorted for better UI
user_input = st.selectbox(
    "Select a movie to get recommendations:",
    movie_titles
)
st.write("You selected:", user_input)

if st.button("Get Recommendations"):
    recommendations = recommend_movies(user_input)

    if recommendations.empty:
        st.error("Movie not found in the database.")
    else:
        st.success(f"Recommendations for '{user_input}':")

        # createing 2 columns
        cols = st.columns(2)

        for index, row in recommendations.iterrows():
            col = cols[index % 2]
            title = row['Series_Title']
            details = get_movie_details(title)
            if details:
                with col:
                    st.subheader(f"**{title}**")
                    st.image(details['posterLink'], width=200)
                    st.write(f"**Overview:** {details['overview']}")
                    st.write(f"**Director:** {details['director']}")
