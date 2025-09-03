from collections import defaultdict
from email.mime.text import MIMEText
import os
import logging
import smtplib
import ssl
import tomllib

from datetime import datetime, timezone, timedelta
from flask import Flask, redirect, render_template, request, g, url_for
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
        SUPPORTER_PAYMENT_URL="http://example.com/supporter"
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
        return render_template("pages/open_day.html")

    from .views import contact
    app.register_blueprint(contact.bp)

    from .views import signup
    app.register_blueprint(signup.bp)

    from .views import report
    app.register_blueprint(report.bp)

    return app