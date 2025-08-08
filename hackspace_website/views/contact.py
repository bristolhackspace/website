from flask import (
    Blueprint, render_template, request, current_app
)
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import BooleanField, StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length

from hackspace_website import mailer, mosparo

bp = Blueprint('contact', __name__, url_prefix="/contact")

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
            validators=[InputRequired(), Length(max=8000)],
            render_kw={"rows": 5}
        )
        privacy = BooleanField(
            Markup(
                'I have read and agree to the terms of the <a href="https://wiki.bristolhackspace.org/policies/privacy" target="_blank"  rel="noopener noreferrer">Privacy Policy</a>'
            ),
            validators=[DataRequired()],
        )

@bp.route("/", methods=["GET", "POST"])
def index():
    form = ContactForm()

    if request.method == "POST":
        if mosparo.verify_formdata():
            if form.validate_on_submit():
                    text = f"{form.name.data.strip()} just sent a message through the contact form:\n\n" + form.message.data

                    mailer.send_internal(
                         reply_to=form.email.data.strip(),
                         subject=f"New message via contact form: {form.subject.data.strip()}",
                         text=text
                    )
                    return render_template(f"pages/contact_success.html")
        else:
            return render_template(f"pages/contact_fail.html")

    return render_template(
        "pages/contact.html",
        form=form,
        mosparo_host=current_app.config["MOSPARO_HOST"],
        mosparo_uuid=current_app.config["MOSPARO_UUID"],
        mosparo_public_key=current_app.config["MOSPARO_PUBLIC_KEY"]
    )