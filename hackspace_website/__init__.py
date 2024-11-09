import os
import logging
import tomllib

from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://postgres:postgres@localhost:5432/website",

    )
    if test_config is None:
        app.config.from_file("config.toml", load=tomllib.load, text=False)
    else:
        app.config.from_mapping(test_config)

    from . import models
    models.init_app(app)

    @app.route("/")
    def home():
        return render_template("pages/home.html")

    @app.route("/visit")
    def visit():
        return render_template("pages/visit.html")

    @app.route("/contact")
    def contact():
        return render_template("pages/contact.html")

    return app