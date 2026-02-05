#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, render_template
import os

DB_PATH = os.environ.get("DB_PATH", "/data/rsvp.db")  # fallback for local testing

# For local testing, you can set:
# DB_PATH = "data/rsvp.db"

DEVELOPMENT_ENV = True

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


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)
