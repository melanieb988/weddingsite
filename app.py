from flask import Flask, render_template, request, jsonify
import os
import psycopg2
import random
from datetime import datetime, timedelta

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
    "html_title": "Melanie & Isaac's Wedding Site",
    "project_name": "Isaac & Melanie's Wedding",
    "keywords": "flask, webapp, basic",
}



@app.route("/gallery")
def gallery():
    gallery_folder = os.path.join(app.static_folder, 'images', 'gallery')

    images = [f for f in os.listdir(gallery_folder)
              if os.path.isfile(os.path.join(gallery_folder, f))]
    images.sort()

    app_data = {
        'description': 'Our Wedding Gallery',
        'keywords': 'wedding, photos, gallery',
        'author': 'Melanie & Isaac',
        'html_title': 'Gallery - Melanie & Isaac',
        'project_name': 'Melanie & Isaac Wedding'
    }

    return render_template('gallery.html', images=images, app_data=app_data)

@app.route("/")
def index():
    image_folder = os.path.join("static", "images", "collage")

    collage_images = []
    if os.path.exists(image_folder):
        collage_images = sorted(
            f for f in os.listdir(image_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        )
        random.shuffle(collage_images)

    return render_template(
        "index.html",
        app_data=app_data,
        collage_images=collage_images
    )


@app.route("/event")
def event():
    return render_template("event.html", app_data=app_data)




@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)

@app.route("/pi_mile")
def pi_mile():
    return render_template("pi_mile.html", app_data=app_data)

@app.route("/travel")
def travel():
    return render_template("travel.html", app_data=app_data)
    
@app.route("/api/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    name_input = data.get("name", "").strip()

    if not name_input:
        return jsonify({"error": "No name provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Split input into first and last name if possible
    parts = name_input.split()
    if len(parts) == 1:
        # Only first name
        cur.execute("""
            SELECT  name, household_id, plus_one_allowed
            FROM guests
            WHERE LOWER(name) LIKE LOWER(%s)
        """, (f"{parts[0]}%",))
    else:
        # Full name search
        cur.execute("""
            SELECT  name, household_id, plus_one_allowed
            FROM guests
            WHERE LOWER(name) = LOWER(%s)
        """, (name_input,))

    results = cur.fetchall()
    cur.close()
    conn.close()

    # Return only the matching people
    guests_list = [
        {
           
            "name": r[0],
            "household_id": r[1],
            "plus_one_allowed": r[2]
        }
        for r in results
    ]

    return jsonify(guests_list)

@app.route("/api/household", methods=["POST"])
def household():
    data = request.get_json()
    household_id = data.get("household_id")
    if not household_id:
        return jsonify({"error": "No household_id provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Include guest_id in the SELECT
    cur.execute("""
        SELECT guest_id, name, attending, meal_choice, plus_one_allowed, plus_one_name, song_rec
        FROM guests
        WHERE household_id = %s
    """, (household_id,))

    results = cur.fetchall()
    cur.close()
    conn.close()

    # Build list including guest_id
    household_list = [
        {
            "guest_id": r[0],       # <-- ADD THIS
            "name": r[1],
            "attending": r[2],
            "meal_choice": r[3],
            "plus_one_allowed": r[4],
            "plus_one_name": r[5],
            "song_rec": r[6]
        }
        for r in results
    ]

    return jsonify(household_list)



# ===== API: Submit RSVP =====
@app.route("/api/rsvp", methods=["POST"])
def rsvp():
    data = request.get_json()
    guests = data.get("guests")  # list of guest updates

    if not guests:
        return jsonify({"error": "No guest data provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    for g in guests:
        guest_id = g.get("guest_id")
        if guest_id is None:
            continue  # skip guests with missing ID

        # Make sure to handle None values properly
        attending = g.get("attending")
        meal_choice = g.get("meal_choice") or None
        dietary_restriction = g.get("dietary_restriction") or None
        plus_one_name = g.get("plus_one_name") or None
        song_rec = g.get("song_rec") or None

        cur.execute("""
            UPDATE guests
            SET attending=%s,
                meal_choice=%s,
                dietary_restriction=%s,
                plus_one_name=%s,
                song_rec=%s,
                last_updated_time=%s
            WHERE guest_id=%s
        """, (
            attending,
            meal_choice,
            dietary_restriction,
            plus_one_name,
            song_rec,
            datetime.utcnow(),
            guest_id
        ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/keepalive')
def keepalive():
    # Convert current UTC to PST
    now_utc = datetime.utcnow()
    now_pst = now_utc - timedelta(hours=8)  # PST = UTC-8
    hour = now_pst.hour

    # Allowed hours: 5 AM → 12 AM PST
    if 5 <= hour <= 23:  # 5 → 23 is 5AM to 11PM; 12 AM = 0, we treat as 23 for simplicity
        return "✅ Site kept alive!"
    else:
        return "💤 Site asleep", 200

if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)

