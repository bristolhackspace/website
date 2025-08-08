from datetime import datetime
from flask import (
    Blueprint, current_app, render_template, request
)
from flask_wtf import FlaskForm
from markupsafe import Markup
import pytz
from wtforms import BooleanField, StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length

from hackspace_website import mailer, mosparo

bp = Blueprint('report', __name__)

class ReportForm(FlaskForm):
        name = StringField(
            "Your name (optional)",
            validators=[Length(max=200)],
        )
        email = EmailField(
            "Your email (optional)",
            validators=[Length(max=200)],
        )
        who = StringField(
            "Who was involved? If you don't know put n/a.",
            validators=[InputRequired(), Length(max=500)],
        )
        when = StringField(
            "When did it happen. Please include the date and time.",
            validators=[InputRequired(), Length(max=500)],
        )
        describe = TextAreaField(
            "Please describe what happened.",
            validators=[InputRequired(), Length(max=10000)],
            render_kw={"rows": 10}
        )
        resources = TextAreaField(
            "Were any first aid/eye wash/spill kit/fire extinguister resources used? Please state what was used.",
            validators=[InputRequired(), Length(max=2000)],
            render_kw={"rows": 2}
        )
        actions = TextAreaField(
            "Have any actions been taken in response to the incident?",
            validators=[InputRequired(), Length(max=5000)],
            render_kw={"rows": 3}
        )
        privacy = BooleanField(
            Markup(
                'I have read and agree to the terms of the <a href="https://wiki.bristolhackspace.org/policies/privacy" target="_blank"  rel="noopener noreferrer">Privacy Policy</a>'
            ),
            validators=[DataRequired()],
        )

@bp.route("/safetyreport", methods=["GET", "POST"])
def report():
    form = ReportForm()

    if request.method == "POST":
        if mosparo.verify_formdata():
            if form.validate_on_submit():
                    name = form.name.data.strip()
                    if not name:
                         name = "Anonymous"
                    text = f"{name} just submitted a safety report.\n\n"
                    text += f"Who was involved: {form.who.data.strip()}\n\n"
                    text += f"When did it happen: {form.when.data.strip()}\n\n"
                    text += f"What happened:\n{form.describe.data.strip()}\n\n"
                    text += f"Were any resources used:\n{form.resources.data.strip()}\n\n"
                    text += f"Have any actions been taken:\n{form.actions.data.strip()}\n\n"


                    tz = pytz.timezone(current_app.config["TIMEZONE"])
                    now = tz.localize(datetime.now().replace(microsecond=0))

                    mailer.send_internal(
                         reply_to=form.email.data.strip(),
                         subject=f"New message via report form (submitted {now.isoformat()})",
                         text=text
                    )
                    return render_template(f"pages/report_success.html")
        else:
            return render_template(f"pages/contact_fail.html")

    return render_template(
        "pages/report.html",
        form=form,
        mosparo_host=current_app.config["MOSPARO_HOST"],
        mosparo_uuid=current_app.config["MOSPARO_UUID"],
        mosparo_public_key=current_app.config["MOSPARO_PUBLIC_KEY"]
    )