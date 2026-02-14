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
# SQLite Database Path Fix
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")


# -----------------------------
# Database Initialization
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY missing in .env file")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY missing in .env file")


# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ✅ Initialize DB at startup (works on Render)
init_db()


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
cosine_sim = cosine_similarity(X, X)


# -----------------------------
# Recommendation Function
# -----------------------------
def get_recommendations(title):
    title = title.lower()

    matches = data[data["movie_title"].str.contains(title)]
    if matches.empty:
        return []

    idx = matches.index[0]

    scores = list(enumerate(cosine_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    top_movies = scores[1:6]
    indices = [i[0] for i in top_movies]

    return data["movie_title"].iloc[indices].tolist()


# -----------------------------
# TMDB Helper Function
# -----------------------------
def tmdb_request(endpoint, params=None):
    url = f"https://api.themoviedb.org/3/{endpoint}"
    params = params or {}
    params["api_key"] = TMDB_API_KEY

    try:
        response = requests.get(url, params=params, timeout=8)

        if response.status_code != 200:
            print("TMDB ERROR:", response.status_code)
            return {"results": []}

        return response.json()

    except Exception as e:
        print("TMDB Request Failed:", e)
        return {"results": []}


# -----------------------------
# API Routes
# -----------------------------
@app.route("/api/popular")
def api_popular():
    return jsonify(tmdb_request("movie/popular"))


@app.route("/api/top")
def api_top():
    return jsonify(tmdb_request("movie/top_rated"))


@app.route("/api/upcoming")
def api_upcoming():
    return jsonify(tmdb_request("movie/upcoming"))


@app.route("/api/genre/<int:genre_id>")
def api_genre(genre_id):
    return jsonify(tmdb_request("discover/movie", {"with_genres": genre_id}))


@app.route("/api/movie/<int:movie_id>")
def api_movie(movie_id):
    return jsonify(tmdb_request(f"movie/{movie_id}"))


@app.route("/search")
def search():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])

    recs = get_recommendations(query)

    results = []
    for title in recs:
        movie = tmdb_request("search/movie", {"query": title})
        if movie.get("results"):
            results.append(movie["results"][0])

    return jsonify(results)


# -----------------------------
# Pages
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/popular")
def popular():
    return render_template("popular.html")


@app.route("/top_rated")
def top_rated():
    return render_template("top_rated.html")


@app.route("/upcoming")
def upcoming():
    return render_template("upcoming.html")


@app.route("/genre/<int:genre_id>")
def genre_page(genre_id):
    return render_template("genre.html", genre_id=genre_id)


# -----------------------------
# Authentication Routes
# -----------------------------
@app.route("/signup", methods=["GET", "POST"])
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    email = request.form["email"]
    password = generate_password_hash(request.form["password"])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
    except:
        return "User already exists"

    conn.close()

    # ✅ After signup → open login popup
    return redirect("/?show_login=1")



@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):
        session["user"] = user[1]
        return redirect("/")

    # ❌ Invalid login → reopen login popup
    return redirect("/?invalid=1")



@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# -----------------------------
# Dialogflow Chatbot Webhook
# -----------------------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    req = request.get_json()

    intent = req["queryResult"]["intent"]["displayName"]
    params = req["queryResult"]["parameters"]

    # ✅ TMDB Genre Mapping
    genre_map = {
        "action": 28,
        "adventure": 12,
        "animation": 16,
        "comedy": 35,
        "drama": 18,
        "fantasy": 14,
        "horror": 27,
        "mystery": 9648,
        "romance": 10749,
        "sci-fi": 878
    }

    # -----------------------------------
    # ✅ Genre Recommendation Intent
    # -----------------------------------
    if intent == "Recommend_By_Genre":

        genre = params.get("genre")

        # ✅ Dialogflow sometimes sends genre as a list
        if isinstance(genre, list):
            genre = genre[0]

        if not genre:
            return jsonify({
                "fulfillmentText": "Please tell me a genre like action, comedy, horror..."
            })

        # Convert genre → TMDB ID
        genre_id = genre_map.get(genre.lower())

        if not genre_id:
            return jsonify({
                "fulfillmentText": f"Sorry, I don’t support genre: {genre}"
            })

        # Fetch top movies from TMDB
        movies_data = tmdb_request("discover/movie", {
            "with_genres": genre_id,
            "sort_by": "popularity.desc"
        })

        movies = movies_data.get("results", [])[:5]

        if not movies:
            return jsonify({
                "fulfillmentText": f"Sorry, I couldn’t find {genre} movies right now."
            })

        # Build Reply
        reply = f"🎬 Top {genre.title()} Movies:\n\n"

        for m in movies:
            reply += f"⭐ {m['title']} ({m['vote_average']}/10)\n"

        return jsonify({
            "fulfillmentText": reply
        })

    # -----------------------------------
    # ✅ Similar Movie Recommendation Intent
    # -----------------------------------
    if intent == "Recommend_Similar_Movie":

        movie_name = params.get("movie")

        # Dialogflow may send movie as list too
        if isinstance(movie_name, list):
            movie_name = movie_name[0]

        if not movie_name:
            return jsonify({
                "fulfillmentText": "Tell me a movie name like Avatar or Titanic."
            })

        recs = get_recommendations(movie_name)

        if not recs:
            return jsonify({
                "fulfillmentText": f"Sorry, I couldn’t find movies like {movie_name}."
            })

        reply = f"🎥 Movies similar to {movie_name.title()}:\n\n"

        for r in recs:
            reply += f"🎬 {r.title()}\n"

        return jsonify({
            "fulfillmentText": reply
        })

    # -----------------------------------
    # Default fallback
    # -----------------------------------
    return jsonify({
        "fulfillmentText": "Try asking: recommend horror movies or recommend movies like Avatar."
    })


# -----------------------------
# Run App (Local Only)
# -----------------------------
if __name__ == "__main__":
    app.run()
