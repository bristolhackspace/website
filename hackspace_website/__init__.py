from collections import defaultdict
from email.mime.text import MIMEText
import os
import logging
import requests
import smtplib
import ssl
import tomllib

from datetime import datetime, timezone, timedelta
from flask import current_app, Flask, redirect, render_template, request, g, url_for
from flask_wtf import FlaskForm
from markupsafe import Markup
from mosparo_api_client import Client as MosparoClient
from wtforms import (
    BooleanField,
    EmailField,
    SubmitField,
    TextAreaField,
    StringField,
    ValidationError,
)
from werkzeug.exceptions import BadRequest
from wtforms.validators import InputRequired, Length, DataRequired


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://postgres:postgres@localhost:5432/website",
        MESSAGE_RATELIMIT_WINDOW=timedelta(minutes=10).total_seconds(),
        MESSAGE_RATELIMIT_COUNT=3,
        RECOMMENDED_PAYMENT_URL="http://example.com/recommended",
        REDUCED_PAYMENT_URL="http://example.com/reduced",
        SUPPORTER_PAYMENT_URL="http://example.com/supporter",
        CMS_OPEN_DAY_URL="http://localhost:8000/api/open-day/test-cms-open-day-2025/"
    )
    if test_config is None:
        app.config.from_file("config.toml", load=tomllib.load, text=False)
    else:
        app.config.from_mapping(test_config)

    @app.route("/")
    def home():
        return render_template("pages/home.html")

    @app.route("/visit")
    def visit():
        return render_template("pages/visit.html")

    @app.route("/open-day")
    def open_day():
        cms_url = current_app.config["CMS_OPEN_DAY_URL"]

        # Default fallback content (your current static version)
        open_day_data = {
            "title": "Bristol Hackspace Open Day",
            "banner_text": "Sorry we have sold out! Unfortunately the interest was far more than we ever anticipated and we have had to limit tickets to avoid overcrowding. We will look at running more open days in the future.",
            "body_html": """
                <p>Join us on Sunday the 31st of August 2025 for our first Open Day in a while! Come see what makes our community and our space tick as well the multitude of tools that could be at your disposal!</p>
                <p>If you've been trying to join us for a while but keep missing tickets, this is your opportunity!</p>
                <p>The main activity for the day will be a stamp rally, collect stamps from each of the areas of the Hackspace and you’ll be able to sign up to the space as a reward! (If you want to! If not you can nab a keyring instead)</p>
            """,
            "date": "2025-08-31",
            "entry_from": "11am",
            "last_entry": "4:30pm",
            "ticket_url": "https://www.ticketsource.co.uk/bristol-hackspace/bristol-hackspace-open-day/e-kjyrxz",
            "accessibility_note": "Please note that we have stairs on entrance and to access other parts of the space.",
        }

        try:
            resp = requests.get(cms_url, timeout=2)
            resp.raise_for_status()
            data = resp.json()

            # Override fallback with real CMS data
            open_day_data.update(data)
        except Exception:
            # Log this in real life, but fall back gracefully
            pass

        return render_template("pages/open_day.html", open_day=open_day_data)

    from .views import contact
    app.register_blueprint(contact.bp)

    from .views import signup
    app.register_blueprint(signup.bp)

    from .views import report
    app.register_blueprint(report.bp)

    return app