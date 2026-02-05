from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import shutil

DB_PATH = "/data/rsvp.db"
LOCAL_DB = "data/rsvp.db"

# Make sure /data exists
os.makedirs("/data", exist_ok=True)

# Copy local DB to persistent disk if it doesn't exist there yet
if not os.path.exists(DB_PATH):
    shutil.copyfile(LOCAL_DB, DB_PATH)


app = Flask(__name__)

app_data = {
    "name": "Melanie & Isaacs Wedding Site",
    "description": "A basic Flask app using bootstrap for our wedding site",
    "author": "Melanie Bowden",
    "html_title": "Melanie & Isaac's Python Wedding Site",
    "project_name": "Beta ",
    "keywords": "flask, webapp, basic",
}


def get_db_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dictionary-like access
    return conn


@app.route("/")
def index():
    return render_template("index.html", app_data=app_data)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)


@app.route("/service")
def service():
    return render_template("service.html", app_data=app_data)


@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)


# ===== API: Lookup Guest by Name =====
@app.route("/api/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"found": False, "error": "No name provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT guest_id, name, household_id, plus_one_allowed FROM guests WHERE name LIKE ?",
        (f"%{name}%",),
    )
    guest = cur.fetchone()
    conn.close()

    if guest:
        return jsonify({
            "found": True,
            "guest_id": guest["guest_id"],
            "name": guest["name"],
            "household_id": guest["household_id"],
            "plus_one_allowed": guest["plus_one_allowed"],
        })
    else:
        return jsonify({"found": False})


# ===== API: Submit RSVP =====
@app.route("/api/rsvp", methods=["POST"])
def submit_rsvp():
    data = request.get_json()
    guest_id = data.get("guest_id")
    attending = data.get("attending")
    meal_choice = data.get("meal_choice")
    plus_one_name = data.get("plus_one_name")
    song_rec = data.get("song_rec")

    if not guest_id:
        return jsonify({"success": False, "error": "Missing guest ID"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE guests
            SET attending = ?, meal_choice = ?, plus_one_name = ?, song_rec = ?
            WHERE guest_id = ?
        """, (attending, meal_choice, plus_one_name, song_rec, guest_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)

