import os
import logging
import tomllib

from flask import Flask, render_template
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import (
    BooleanField,
    EmailField,
    TextAreaField,
    StringField,
    ValidationError,
)
from wtforms.validators import InputRequired, Length, DataRequired

from hackspace_website.models import db, Message


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

    class ContactForm(FlaskForm):
        name = StringField(
            "Name",
            name="iy5ku",
            validators=[InputRequired(), Length(max=Message.name.type.length)],
        )
        email = EmailField(
            "Email",
            name="oeu2b",
            validators=[InputRequired(), Length(max=Message.email.type.length)],
        )
        subject = StringField(
            "Subject",
            name="tx5jm",
            validators=[InputRequired(), Length(max=Message.subject.type.length)],
        )
        message = TextAreaField(
            "Message",
            name="fc2ah",
            validators=[InputRequired(), Length(max=Message.message.type.length)],
        )
        privacy = BooleanField(
            Markup(
                'I have read and agree to the terms of the <a href="https://wiki.bristolhackspace.org/policies/privacy">Privacy Policy</a>'
            ),
            name="um90x",
            validators=[DataRequired()],
        )
        honeypot = BooleanField("Fax only", name="contact_me_by_fax_only")

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = ContactForm()

        if form.validate_on_submit():
            return render_template("pages/contact_success.html")

        return render_template("pages/contact.html", form=form)

    return app
