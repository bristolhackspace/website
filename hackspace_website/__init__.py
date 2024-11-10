from collections import defaultdict
import os
import logging
import tomllib

from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request
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
        MESSAGE_RATELIMIT_WINDOW=timedelta(minutes=10).total_seconds(),
        MESSAGE_RATELIMIT_COUNT=3,
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
            message = Message(
                name=form.name.data,
                email=form.email.data,
                subject=form.subject.data,
                message=form.message.data,
                ip_addr=request.remote_addr,
                user_agent=request.user_agent.string,
                honeypot_triggered=form.honeypot.data,
                received=datetime.now(timezone.utc)
            )
            db.session.add(message)
            db.session.commit()
            return render_template("pages/contact_success.html")

        return render_template("pages/contact.html", form=form)

    @app.cli.command("process-emails")
    def process_emails(name):
        query = db.session.query(Message).where(Message.processed == False).order_by(Message.received)
        messages: list[Message] = db.session.execute(query).scalars()

        now = datetime.now(timezone.utc)

        messages_by_ip = defaultdict(list)

        ratelimit_window = app.config["MESSAGE_RATELIMIT_WINDOW"]
        ratelimit_max_count = app.config["MESSAGE_RATELIMIT_WINDOW"]

        for message in messages:
            messages_by_ip[message.ip_addr].append(message)
            if (now - message.received).total_seconds() < ratelimit_window:
                continue

            message.processed = True

            if message.honeypot_triggered:
                message.rejected = True
                continue


        for _ip, messages in messages_by_ip.items():
            window_head = iter(messages)
            window_start_time = next(window_head).received
            window_count = 0

            reject=False

            for message in messages:
                # Increment ratelimit window if message was received outside of it
                while (message.received - window_start_time).total_seconds() > ratelimit_window:
                    window_count -= 1
                    window_start_time = next(window_head).received

                window_count += 1

                if window_count >= ratelimit_max_count:
                    reject = True
                    break

            if reject:
                for message in messages:
                    message.rejected = True


        for message in messages:
            if message.processed == False or message.rejected == True:
                continue
            print(f"Sending message '{message.subject}'")




    return app
