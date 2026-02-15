import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify, render_template
import pandas as pd
import requests

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, flash



# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("❌ TMDB_API_KEY not found. Add it in your .env file")


# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
app.secret_key = "cinesmart_secret_key"





# -----------------------------
# Load Dataset
# -----------------------------
data = pd.read_csv("final_data.csv")
print("✅ CSV Loaded Successfully")

data["movie_title"] = data["movie_title"].str.lower()

# Combine features for recommendation
data["comb"] = (
    data["director_name"].fillna("") + " " +
    data["actor_1_name"].fillna("") + " " +
    data["actor_2_name"].fillna("") + " " +
    data["actor_3_name"].fillna("") + " " +
    data["genres"].fillna("")
)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    ngram_range=(1, 2)
)

X_vectorized = vectorizer.fit_transform(data["comb"])

# Cosine Similarity
cosine_sim = cosine_similarity(X_vectorized, X_vectorized)


# -----------------------------
# Recommendation Function
# -----------------------------
def get_recommendations(movie_title):
    movie_title = movie_title.lower()

    if movie_title not in data["movie_title"].values:
        return []

    idx = data.index[data["movie_title"] == movie_title][0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    top_movies = sim_scores[1:10]  # skip itself
    movie_indices = [i[0] for i in top_movies]

    return data["movie_title"].iloc[movie_indices].tolist()


# -----------------------------
# TMDB Fetch Function
# -----------------------------
def fetch_tmdb_movie(title):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": title}

        response = requests.get(url, params=params, timeout=5)

        if response.status_code != 200:
            return None

        results = response.json().get("results", [])
        return results[0] if results else None

    except Exception as e:
        print("❌ TMDB ERROR:", e)
        return None


# -----------------------------
# Search API Route
# -----------------------------
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")

    if not query:
        return jsonify([])

    recommendations = get_recommendations(query)

    results = []

    # First show searched movie
    first_movie = fetch_tmdb_movie(query)
    if first_movie:
        results.append(first_movie)

    # Then show recommendations
    for title in recommendations[:5]:
        movie = fetch_tmdb_movie(title)
        if movie:
            results.append(movie)

    return jsonify(results)

# -----------------------------
# Database Intialization
# -----------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# -----------------------------
# Main Pages Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("mi.html")


@app.route("/popular")
def popular():
    return render_template("popular.html")


@app.route("/top_rated")
def top_rated():
    return render_template("top_rated.html")


@app.route("/upcoming")
def upcoming():
    return render_template("upcoming.html")


# -----------------------------
# ✅ Genre Routes (FIXED)
# -----------------------------
@app.route("/action")
def action():
    return render_template("action.html")


@app.route("/adventure")
def adventure():
    return render_template("adventure.html")


@app.route("/animation")
def animation():
    return render_template("animation.html")


@app.route("/comedy")
def comedy():
    return render_template("comedy.html")


@app.route("/drama")
def drama():
    return render_template("drama.html")


@app.route("/fantasy")
def fantasy():
    return render_template("fantasy.html")


@app.route("/horror")
def horror():
    return render_template("horror.html")


@app.route("/mystery")
def mystery():
    return render_template("mystery.html")


@app.route("/romance")
def romance():
    return render_template("romance.html")


@app.route("/scifi")
def scifi():
    return render_template("scifi.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if empty
    if not username or not email or not password:
        return "All fields are required!"

    # Hash password
    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    except sqlite3.IntegrityError:
        return "Email already registered!"

@app.route("/login", methods=["GET", "POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    conn.close()

    # If user exists and password matches
    if user and check_password_hash(user[3], password):
        session["user"] = user[1]  # username
        return redirect("/")

    return "Invalid email or password!"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# -----------------------------
# Run Locally
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)



