from flask import Flask, render_template, request, jsonify
import os
import psycopg2

app = Flask(__name__)

# Get database URL from environment variable
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise Exception("DATABASE_URL not set!")

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn



app = Flask(__name__)

app_data = {
    "name": "Melanie & Isaacs Wedding Site",
    "description": "A basic Flask app using bootstrap for our wedding site",
    "author": "Melanie Bowden",
    "html_title": "Melanie & Isaac's Python Wedding Site",
    "project_name": "Beta ",
    "keywords": "flask, webapp, basic",
}





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
    name_input = data.get("name", "").strip()
    
    if not name_input:
        return jsonify({"error": "No name provided"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1️⃣ Find the household_id for the searched name
    cur.execute("""
        SELECT household_id
        FROM guests
        WHERE LOWER(name) LIKE LOWER(%s)
        LIMIT 1
    """, (f"%{name_input}%",))
    
    row = cur.fetchone()
    
    if not row:
        cur.close()
        conn.close()
        return jsonify([])  # no guest found
    
    household_id = row[0]
    
    # 2️⃣ Get ALL guests in that household
    cur.execute("""
        SELECT name, household_id, plus_one_allowed, attending, meal_choice, plus_one_name, song_rec
        FROM guests
        WHERE household_id = %s
        ORDER BY name
    """, (household_id,))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    guests_list = [
        {
            "name": r[0],
            "household_id": r[1],
            "plus_one_allowed": r[2],
            "attending": r[3],
            "meal_choice": r[4],
            "plus_one_name": r[5],
            "song_rec": r[6]
        }
        for r in results
    ]
    
    return jsonify(guests_list)




# ===== API: Submit RSVP =====
@app.route("/api/rsvp", methods=["POST"])
def rsvp():
    data = request.get_json()
    guests = data.get("guests")  # list of guests with updates

    if not guests:
        return jsonify({"error": "No guest data provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    for g in guests:
        cur.execute("""
            UPDATE guests
            SET attending=%s, meal_choice=%s, plus_one_name=%s, song_rec=%s
            WHERE name=%s
        """, (
            g.get("attending"),
            g.get("meal_choice"),
            g.get("plus_one_name"),
            g.get("song_rec"),
            g.get("name")
        ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success"})



if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)

