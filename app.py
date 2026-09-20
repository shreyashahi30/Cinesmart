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

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Works without it, but sessions are forgeable until you set a real
    # SECRET_KEY in your .env file. See the note at the end of this reply.
    print("WARNING: SECRET_KEY not set in .env — using an insecure default.")
    SECRET_KEY = "insecure-dev-key-change-me"

TMDB_TIMEOUT = 8  # seconds


# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY


# -----------------------------
# TMDB helper (centralized error handling)
# -----------------------------
def tmdb_get(url, params=None):
    """Wraps every TMDB call so a timeout / rate limit / bad response
    can't crash a route with an uncaught exception."""
    try:
        res = requests.get(url, params=params, timeout=TMDB_TIMEOUT)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"TMDB request failed: {e}")
        return None
    except ValueError as e:
        print(f"TMDB returned invalid JSON: {e}")
        return None


# -----------------------------
# Load Dataset
# -----------------------------
data = pd.read_csv("final_data.csv")
data["movie_title"] = data["movie_title"].str.lower()

# Genres are repeated so genre overlap carries real weight in the TF-IDF
# vector. Previously a single genre word was drowned out by rare actor
# surnames, so recommendations tracked shared cast more than shared genre.
data["comb"] = (
    data["director_name"].fillna("") + " " +
    data["actor_1_name"].fillna("") + " " +
    data["actor_2_name"].fillna("") + " " +
    data["actor_3_name"].fillna("") + " " +
    ((data["genres"].fillna("") + " ") * 3)
)

vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
X = vectorizer.fit_transform(data["comb"])
cosine_sim = cosine_similarity(X)


# -----------------------------
# Recommendation Function
# -----------------------------
def get_recommendations(title):
    title = title.lower().strip()

    if not title:
        return []

    # regex=False: a title containing "(", ")", "+", etc. used to crash
    # this with an uncaught re.error and 500 the whole route.
    matches = data[data["movie_title"].str.contains(title, na=False, regex=False)]

    if matches.empty:
        return []

    idx = matches.index[0]

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

    result = tmdb_get(url, params)
    if not result:
        return None

    results = result.get("results", [])
    return results[0] if results else None


# -----------------------------
# Search API
# -----------------------------
@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

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


init_db()

# -----------------------------
# Main Pages
# -----------------------------
@app.route("/")
def home():
    return render_template("mi.html", username=session.get("user"))


@app.route("/popular")
def popular():
    return render_template("popular.html", username=session.get("user"))


@app.route("/top_rated")
def top_rated():
    return render_template("top_rated.html", username=session.get("user"))


@app.route("/upcoming")
def upcoming():
    return render_template("upcoming.html", username=session.get("user"))


# -----------------------------
# TMDB API Routes
# -----------------------------
@app.route("/api/popular")
def api_popular():
    url = "https://api.themoviedb.org/3/movie/popular"
    result = tmdb_get(url, {"api_key": TMDB_API_KEY})
    return jsonify(result or {"results": []})


@app.route("/api/top")
def api_top():
    url = "https://api.themoviedb.org/3/movie/top_rated"
    result = tmdb_get(url, {"api_key": TMDB_API_KEY})
    return jsonify(result or {"results": []})


@app.route("/api/upcoming")
def api_upcoming():
    url = "https://api.themoviedb.org/3/movie/upcoming"
    result = tmdb_get(url, {"api_key": TMDB_API_KEY})
    return jsonify(result or {"results": []})


@app.route("/api/genre/<int:genre_id>")
def api_genre(genre_id):
    url = "https://api.themoviedb.org/3/discover/movie"
    result = tmdb_get(url, {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
    })
    return jsonify(result or {"results": []})


@app.route("/api/movie/<int:movie_id>")
def api_movie_details(movie_id):
    """Used by the movie-detail modal on every page (popular/top/upcoming/genre)."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    result = tmdb_get(url, {"api_key": TMDB_API_KEY, "language": "en-US"})
    if not result:
        return jsonify({"error": "Could not fetch movie details"}), 502
    return jsonify(result)


# -----------------------------
# Genre Pages
# -----------------------------
@app.route("/action")
def action():
    return render_template("action.html", username=session.get("user"))


@app.route("/adventure")
def adventure():
    return render_template("adventure.html", username=session.get("user"))


@app.route("/animation")
def animation():
    return render_template("animation.html", username=session.get("user"))


@app.route("/comedy")
def comedy():
    return render_template("comedy.html", username=session.get("user"))


@app.route("/drama")
def drama():
    return render_template("drama.html", username=session.get("user"))


@app.route("/fantasy")
def fantasy():
    return render_template("fantasy.html", username=session.get("user"))


@app.route("/horror")
def horror():
    return render_template("horror.html", username=session.get("user"))


@app.route("/mystery")
def mystery():
    return render_template("mystery.html", username=session.get("user"))


@app.route("/romance")
def romance():
    return render_template("romance.html", username=session.get("user"))


@app.route("/scifi")
def scifi():
    return render_template("scifi.html", username=session.get("user"))


# -----------------------------
# Signup
# -----------------------------
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not username or not email or not password:
        return "Username, email and password are all required", 400

    hashed_pw = generate_password_hash(password)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Email already exists", 400
    except sqlite3.Error as e:
        conn.close()
        return f"Signup failed: {e}", 500

    conn.close()
    session["user"] = username
    return redirect("/")


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):
        session["user"] = user[1]
        return redirect("/")

    return "Invalid credentials", 401


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# -----------------------------
# Chatbot Route
# -----------------------------
GENRE_MAP = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "drama": 18,
    "fantasy": 14,
    "horror": 27,
    "mystery": 9648,
    "romance": 10749,
    "sci-fi": 878,
    "scifi": 878,
    "science fiction": 878,
}


@app.route("/chatbot", methods=["POST"])
def chatbot():
    body = request.get_json(silent=True) or {}
    message = str(body.get("message", "")).strip()

    if not message:
        return jsonify({
            "reply": "Ask me something like:\n- movies like Avatar\n- suggest horror movies"
        })

    lower_msg = message.lower()

    # -----------------------------
    # GENRE → TMDB Recommendations
    # -----------------------------
    matched_genre = None
    for genre_name, genre_id in GENRE_MAP.items():
        if genre_name in lower_msg:
            matched_genre = (genre_name, genre_id)
            break

    if matched_genre:
        genre_name, genre_id = matched_genre

        url = "https://api.themoviedb.org/3/discover/movie"
        result = tmdb_get(url, {
            "api_key": TMDB_API_KEY,
            "with_genres": genre_id,
            "sort_by": "popularity.desc"
        })

        movies = (result or {}).get("results", [])[:5]

        if not movies:
            return jsonify({
                "reply": f"Sorry, I couldn't find any {genre_name} movies right now."
            })

        reply = f"🎬 Here are some popular {genre_name} movies:\n\n"
        for m in movies:
            reply += f"⭐ {m['title']} (Rating: {m['vote_average']})\n"

        return jsonify({"reply": reply})

    # -----------------------------
    # SIMILAR MOVIE → CSV Dataset
    # -----------------------------
    movie_name = None
    for keyword in ("similar to", "movies like", "movie like", "like", "recommend"):
        if keyword in lower_msg:
            movie_name = lower_msg.split(keyword, 1)[1].strip()
            break

    if not movie_name:
        movie_name = lower_msg

    movie_name = movie_name.strip(" ?.!")

    if movie_name:
        recommendations = get_recommendations(movie_name)

        if recommendations:
            reply = f"🎥 Movies similar to {movie_name.title()}:\n\n"
            for r in recommendations:
                reply += f"👉 {r.title()}\n"
            return jsonify({"reply": reply})

    # -----------------------------
    # DEFAULT FALLBACK
    # -----------------------------
    return jsonify({
        "reply": "Sorry, I couldn't quite understand that. Try:\n- \"suggest horror movies\"\n- \"movies like Avatar\""
    })

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
