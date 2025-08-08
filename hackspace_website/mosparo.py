from flask import Flask, current_app, g, request
from flask_wtf import FlaskForm
from werkzeug.local import LocalProxy
from mosparo_api_client import Client as MosparoClient


def get_client():
    if 'mosparo' not in g:
        g.mosparo = MosparoClient(current_app.config["MOSPARO_HOST"], current_app.config["MOSPARO_PUBLIC_KEY"], current_app.config["MOSPARO_PRIVATE_KEY"])
    return g.mosparo

client = LocalProxy(get_client)


def verify_formdata():
    formdata = request.form.copy()
    mosparo_submit_token = formdata['_mosparo_submitToken']
    mosparo_validation_token = formdata['_mosparo_validationToken']
    result = client.verify_submission(formdata, mosparo_submit_token, mosparo_validation_token)
    return result.is_submittable()