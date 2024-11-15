from collections import defaultdict
from email.mime.text import MIMEText
import os
import logging
import smtplib
import ssl
import tomllib

from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, g
from flask_wtf import FlaskForm
from markupsafe import Markup
from mosparo_api_client import Client as MosparoClient
from wtforms import (
    BooleanField,
    EmailField,
    TextAreaField,
    StringField,
    ValidationError,
)
from wtforms.validators import InputRequired, Length, DataRequired


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://postgres:postgres@localhost:5432/website",
        MESSAGE_RATELIMIT_WINDOW=timedelta(minutes=10).total_seconds(),
        MESSAGE_RATELIMIT_COUNT=3,
    )
    if test_config is None:
        app.config.from_file("config.toml", load=tomllib.load, text=False)
    else:
        app.config.from_mapping(test_config)

    mosparo_client = MosparoClient(app.config["MOSPARO_HOST"], app.config["MOSPARO_PUBLIC_KEY"], app.config["MOSPARO_PRIVATE_KEY"])

    @app.route("/")
    def home():
        return render_template("pages/home.html")

    @app.route("/visit")
    def visit():
        return render_template("pages/visit.html")

    class ContactForm(FlaskForm):
        name = StringField(
            "Name",
            validators=[InputRequired(), Length(max=200)],
        )
        email = EmailField(
            "Email",
            validators=[InputRequired(), Length(max=200)],
        )
        subject = StringField(
            "Subject",
            validators=[InputRequired(), Length(max=500)],
        )
        message = TextAreaField(
            "Message",
            validators=[InputRequired(), Length(max=5000)],
        )
        privacy = BooleanField(
            Markup(
                'I have read and agree to the terms of the <a href="https://wiki.bristolhackspace.org/policies/privacy" target="_blank"  rel="noopener noreferrer">Privacy Policy</a>'
            ),
            validators=[DataRequired()],
        )

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = ContactForm()

        if request.method == "POST":
            formdata = request.form.copy()
            mosparo_submit_token = formdata['_mosparo_submitToken']
            mosparo_validation_token = formdata['_mosparo_validationToken']
            result = mosparo_client.verify_submission(formdata, mosparo_submit_token, mosparo_validation_token)
            if result.is_submittable():
                if form.validate_on_submit():
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(app.config["SMTP_SERVER"], app.config["SMTP_PORT"], context=context) as smtp_client:
                        smtp_client.login(app.config["SMTP_EMAIL"], app.config["SMTP_PASSWORD"])
                        sender_email = app.config["SMTP_EMAIL"]
                        receiver_email = app.config["SMTP_EMAIL"]
                        reply_to = form.email.data.strip()

                        text = f"{form.name.data.strip()} just sent a message through the contact form:\n\n" + form.message.data

                        message = MIMEText(text, "plain")
                        message["Subject"] = f"New message via contact form: {form.subject.data.strip()}"
                        message["From"] = sender_email
                        message["To"] = receiver_email
                        message['reply-to'] = reply_to
                        smtp_client.sendmail(sender_email, receiver_email, message.as_string())

                    return render_template("pages/contact_success.html")
            else:
                return render_template("pages/contact_fail.html")

        return render_template("pages/contact.html", form=form)




    return app
