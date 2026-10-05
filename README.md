# Movie Recommender System

An end-to-end Machine Learning project built using Python, Streamlit, and the TMDB 5000 Movies Dataset. The application recommends similar movies based on content metadata features (genres, keywords, cast, and crew) calculated via Cosine Similarity scores.

## Features
- **Content-Based Filtering:** Uses `CountVectorizer` (Bag of Words) to parse and clean text data metadata.
- **Similarity Scoring:** Measures structural cosine distance vectors between movies.
- **Interactive Web App:** Developed with a Streamlit interface that pulls live graphic movie posters dynamically using the TMDB API.

## Technical Stack
- **Languages & Frameworks:** Python, Streamlit
- **Libraries:** Pandas, NumPy, Scikit-Learn, Requests, Pickle

## How to Run Locally
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Boot up the local development web server:
   ```bash
   streamlit run app.py
   ```