from collections import defaultdict
from email.mime.text import MIMEText
import os
import logging
import re
import requests
import smtplib
import ssl
import tomllib

from bs4 import BeautifulSoup
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

YOUTUBE_ID_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,})"
)

def _youtube_iframe(video_id: str) -> str:
    src = f"https://www.youtube.com/embed/{video_id}"
    return (
        '<div class="video-embed">'
        f'<iframe width="560" height="315" '
        f'src="{src}" '
        'title="YouTube video player" '
        'frameborder="0" '
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
        'referrerpolicy="strict-origin-when-cross-origin" '
        'allowfullscreen></iframe>'
        '</div>'
    )

def embed_youtube_links(html: str) -> str:
    if not html:
        return html

    soup = BeautifulSoup(html, "lxml")

    # Replace <a href="youtube...">something</a> with iframe container
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = YOUTUBE_ID_RE.search(href)
        if not m:
            continue

        video_id = m.group(1)

        # If the URL is also in the text, we still replace the whole anchor
        a.replace_with(BeautifulSoup(_youtube_iframe(video_id), "lxml"))

    # Also handle bare text URLs not wrapped in <a>
    # (Optional, but nice)
    for text_node in soup.find_all(string=True):
        if not text_node or "youtube" not in text_node:
            continue

        m = YOUTUBE_ID_RE.search(str(text_node))
        if not m:
            continue

        video_id = m.group(1)
        # Replace the text node with an iframe
        text_node.replace_with(BeautifulSoup(_youtube_iframe(video_id), "lxml"))

    # BeautifulSoup wraps in <html><body> sometimes; return body contents if present
    body = soup.body
    return "".join(str(x) for x in (body.contents if body else soup.contents))


def absolutize_cms_media(html: str, cms_base_url: str) -> str:
    if not html:
        return html
    return html.replace('src="/media/', f'src="{cms_base_url}/media/')

# Match /media/... or http(s)://.../media/... ending in a common image extension
IMAGE_PATH_RE = re.compile(
    r"^(https?://[^\"'<>\s]+)?/media/[^\"'<>\s]+\.(png|jpg|jpeg|gif|webp|svg)$",
    re.IGNORECASE,
)

def _make_img_tag(src: str) -> str:
    return f'<img class="blog-body-image" src="{src}" alt="">'

def embed_cms_images(html: str, cms_base_url: str) -> str:
    if not html:
        return html

    soup = BeautifulSoup(html, "lxml")

    # 1) Replace <a href="/media/...png">...</a> with <img ...>
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not IMAGE_PATH_RE.match(href):
            continue

        # absolutize relative /media/... to the CMS base URL
        if href.startswith("/media/"):
            href = cms_base_url.rstrip("/") + href

        a.replace_with(BeautifulSoup(_make_img_tag(href), "lxml"))

    # 2) Replace bare text nodes that look like /media/...png with <img ...>
    for text_node in soup.find_all(string=True):
        text = (str(text_node) or "").strip()
        if not text:
            continue

        if not IMAGE_PATH_RE.match(text):
            continue

        src = text
        if src.startswith("/media/"):
            src = cms_base_url.rstrip("/") + src

        text_node.replace_with(BeautifulSoup(_make_img_tag(src), "lxml"))

    # Return inner HTML (avoid soup wrapping)
    body = soup.body
    return "".join(str(x) for x in (body.contents if body else soup.contents))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://postgres:postgres@localhost:5432/website",
        MESSAGE_RATELIMIT_WINDOW=timedelta(minutes=10).total_seconds(),
        MESSAGE_RATELIMIT_COUNT=3,
        RECOMMENDED_PAYMENT_URL="http://example.com/recommended",
        REDUCED_PAYMENT_URL="http://example.com/reduced",
        SUPPORTER_PAYMENT_URL="http://example.com/supporter",
        CMS_BASE_URL="http://localhost:8000",
        CMS_OPEN_DAY_URL="http://localhost:8000/api/open-day/test-cms-open-day-2025/",
        CMS_BLOG_LIST_URL="http://localhost:8000/api/blog/",
        CMS_BLOG_DETAIL_URL="http://localhost:8000/api/blog/{slug}/",
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

    @app.route("/blog")
    def blog_index():
        cms_url = current_app.config["CMS_BLOG_LIST_URL"]

        posts = []

        try:
            resp = requests.get(cms_url, timeout=2)
            resp.raise_for_status()
            posts = resp.json()
        except Exception as e:
            print(e)
            # In production you’d log this; here we just show empty list / message
            posts = []

        return render_template("blog/index.html", posts=posts)

    @app.route("/blog/<slug>")
    def blog_detail(slug):
        cms_url = current_app.config["CMS_BLOG_DETAIL_URL"].format(slug=slug)

        post = None
        try:
            resp = requests.get(cms_url, timeout=2)
            resp.raise_for_status()
            post = resp.json()
        except Exception:
            # Could render a 404 or a friendly error page
            return render_template("blog/not_found.html", slug=slug), 404

        post["body_html"] = post.get("body_html", "")
        post["body_html"] = embed_cms_images(post["body_html"], current_app.config["CMS_BASE_URL"])
        post["body_html"] = embed_youtube_links(post["body_html"])
        return render_template("blog/detail.html", post=post)

    from .views import contact
    app.register_blueprint(contact.bp)

    from .views import signup
    app.register_blueprint(signup.bp)

    from .views import report
    app.register_blueprint(report.bp)

    return app
