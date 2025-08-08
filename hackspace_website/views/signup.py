from flask import (
    Blueprint, render_template, redirect, current_app
)
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import BooleanField, SubmitField
from werkzeug.exceptions import BadRequest
from wtforms.validators import DataRequired

bp = Blueprint('signup', __name__, url_prefix="/dd-signup")

class SignupForm(FlaskForm):
        visited = BooleanField(
            "I have already visited hackspace and know what I'm getting into",
            validators=[DataRequired()],
        )
        over18 = BooleanField(
            "I confirm I am over the age of 18",
            validators=[DataRequired()],
        )
        terms = BooleanField(
            Markup(
                'I have read and agree to the <a href="https://wiki.bristolhackspace.org/policies/home" target="_blank"  rel="noopener noreferrer">Terms & Conditions</a>'
            ),
            validators=[DataRequired()],
        )
        privacy = BooleanField(
            Markup(
                'I have read and agree to the <a href="https://wiki.bristolhackspace.org/policies/privacy" target="_blank"  rel="noopener noreferrer">Privacy Policy</a>'
            ),
            validators=[DataRequired()],
        )
        recommended = SubmitField("Recommended payment of £15 per month")
        reduced = SubmitField("Reduced payment of £5 per month")

@bp.route("/", methods=["GET", "POST"])
def index():
    form = SignupForm()

    if form.validate_on_submit():
        if form.recommended.data:
            url = current_app.config["RECOMMENDED_PAYMENT_URL"]
        elif form.reduced.data:
            url = current_app.config["REDUCED_PAYMENT_URL"]
        else:
            raise BadRequest("Must submit recommended or reduced button")
        return redirect(url)
    return render_template("pages/signup.html", form=form)