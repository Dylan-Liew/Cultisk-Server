from functools import wraps
from flask import request, jsonify, make_response
from requests_oauthlib import OAuth2Session
from google.oauth2 import id_token
from google.auth.transport import requests
from google.oauth2.credentials import Credentials
from cultisk import db
from cultisk.Models import OAuth2User
from cultisk.config import Auth


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(Auth.CLIENT_ID, state=state, redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(Auth.CLIENT_ID, redirect_uri=Auth.REDIRECT_URI, scope=Auth.SCOPE)
    return oauth


def get_openid_identity():
    auth_header_value = request.headers.get('Authorization', None)

    try:
        token = auth_header_value.split()[1]
        payload = id_token.verify_oauth2_token(token, requests.Request(), Auth.CLIENT_ID)
        return payload["sub"]
    except ValueError as e:
        return make_response(jsonify({"error": f'Invalid token, {str(e)}'}),
                             401)


def openid_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        auth_header_value = request.headers.get('Authorization', None)

        if auth_header_value is None:
            return make_response(jsonify({"error": 'Authorization Required, Request does not contain an access token'}),
                                 401)

        try:
            token = auth_header_value.split()[1]
            payload = id_token.verify_oauth2_token(token, requests.Request(), Auth.CLIENT_ID)
        except ValueError as e:
            return make_response(jsonify({"error": f'Invalid token, {str(e)}', "expired": True}),
                                 401)
        return func(*args, **kwargs)

    return decorator


def refresh_g_access_token(cred):
    credentials = Credentials(**cred)
    credentials.refresh(requests.Request())
    cred = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
    }
    payload = id_token.verify_oauth2_token(credentials.id_token, requests.Request(), Auth.CLIENT_ID)
    oauth2_user = OAuth2User.query.filter_by(sub=payload["sub"]).first()
    oauth2_user.token = credentials.id_token
    db.session.commit()
    return cred, credentials.id_token
