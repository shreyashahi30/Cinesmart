import os
import sqlite3
import requests
import pandas as pd

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env file")


# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__)
app.secret_key = "cinesmart_secret_key"


# -----------------------------
# Load Dataset
# -----------------------------
data = pd.read_csv("final_data.csv")
data["movie_title"] = data["movie_title"].str.lower()

data["comb"] = (
    data["director_name"].fillna("") + " " +
    data["actor_1_name"].fillna("") + " " +
    data["actor_2_name"].fillna("") + " " +
    data["actor_3_name"].fillna("") + " " +
    data["genres"].fillna("")
)

vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
X = vectorizer.fit_transform(data["comb"])
cosine_sim = cosine_similarity(X)


# -----------------------------
# Recommendation Function
# -----------------------------
def get_recommendations(title):
    title = title.lower()

    if title not in data["movie_title"].values:
        return []

    idx = data.index[data["movie_title"] == title][0]
    scores = list(enumerate(cosine_sim[idx]))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_movies = scores[1:6]

    return [data["movie_title"].iloc[i[0]] for i in top_movies]


# -----------------------------
# TMDB Movie Fetch
# -----------------------------
def fetch_tmdb_movie(title):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title}

    res = requests.get(url, params=params)
    results = res.json().get("results", [])

    return results[0] if results else None


# -----------------------------
# Search API
# -----------------------------
@app.route("/search")
def search():
    query = request.args.get("query")

    if not query:
        return jsonify([])

    recommendations = get_recommendations(query)
    results = []

    first = fetch_tmdb_movie(query)
    if first:
        results.append(first)

    for rec in recommendations:
        movie = fetch_tmdb_movie(rec)
        if movie:
            results.append(movie)

    return jsonify(results)


# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Main Pages
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
# TMDB API Routes (ADDED)
# -----------------------------
@app.route("/api/popular")
def api_popular():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    return jsonify(requests.get(url).json())


@app.route("/api/top")
def api_top():
    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}"
    return jsonify(requests.get(url).json())


@app.route("/api/upcoming")
def api_upcoming():
    url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={TMDB_API_KEY}"
    return jsonify(requests.get(url).json())


@app.route("/api/genre/<int:genre_id>")
def api_genre(genre_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}"
    return jsonify(requests.get(url).json())


# -----------------------------
# Genre Pages
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


# -----------------------------
# Signup
# -----------------------------
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    hashed_pw = generate_password_hash(password)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
    except:
        return "Email already exists"

    conn.close()
    return redirect("/")


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):
        session["user"] = user[1]
        return redirect("/")

    return "Invalid credentials"


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# -----------------------------
# Dialogflow Webhook Route
# -----------------------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    req = request.get_json()

    user_text = req["queryResult"]["queryText"]

    recommendations = get_recommendations(user_text)

    if not recommendations:
        reply = "Sorry, I couldn't find similar movies."
    else:
        reply = "Movies like that: " + ", ".join(recommendations)

    return jsonify({
        "fulfillmentText": reply
    })


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
