import json
from flask import request, session, render_template, make_response
from google.oauth2 import id_token
from google.auth.transport import requests
from google.oauth2 import credentials
from flask_restx import Namespace, Resource
from requests import HTTPError

from cultisk import db, Auth
from cultisk.helper import get_google_auth, refresh_g_access_token
from cultisk.Models import AppSession, OAuth2User

api = Namespace("callback", description="Auth related")


@api.route("/auth-callback/")
class GoogleCallback(Resource):

    def get(self):
        if "error" in request.args:
            if request.args.get('error') == 'access_denied':
                return make_response(render_template("auth_done.html", error=True), 500)
            return make_response(render_template("auth_done.html", error=True), 401)
        if 'code' not in request.args and 'state' not in request.args:
            return {}, 404
        else:
            # Execution reaches here when user has successfully authenticated our app.
            google = get_google_auth(state=session['oauth_state'])
            try:
                token = google.fetch_token(Auth.TOKEN_URI, client_secret=Auth.CLIENT_SECRET,
                                           authorization_response=request.url)
            except HTTPError:
                return make_response(render_template("auth_done.html", error=True), 500)
            google = get_google_auth(token=token)
            resp = google.get(Auth.USER_INFO)
            if resp.status_code == 200:
                user_data = resp.json()
                decoded_token = id_token.verify_oauth2_token(token["id_token"], requests.Request(), Auth.CLIENT_ID)
                oauth_user = OAuth2User()
                oauth_user.email = user_data["email"]
                oauth_user.sub = decoded_token["sub"]
                cred = {
                    'token': token["access_token"],
                    'refresh_token': token["refresh_token"],
                    'token_uri': Auth.TOKEN_URI,
                    'client_id': Auth.CLIENT_ID,
                    'client_secret': Auth.CLIENT_SECRET,
                    'scopes': token["scope"]
                }
                oauth_user.credentials = json.dumps(cred)
                oauth_user.token = token["id_token"]
                db.session.add(oauth_user)
                db.session.commit()
                c_session = AppSession()
                c_session.uuid = session["app_id"]
                c_session.os_version = session["os_version"]
                c_session.oauth2_user_sub = decoded_token["sub"]
                c_session.device_hostname = session["device_hostname"]
                db.session.add(c_session)
                db.session.commit()
                return make_response(render_template("auth_done.html", error=False), 200)
            else:
                return make_response(render_template("auth_done.html", error=True), 500)


@api.route("/app-auth/")
class AppAuthComplete(Resource):

    def get(self):
        data = {"success": True}
        app_id = request.args.get("app_id")
        s: AppSession = AppSession.query.filter_by(uuid=app_id).first()
        if s is None:
            data["success"] = False
            data["authenticated"] = False
            return data, 404
        elif s.oauth2_user.token is None:
            data["success"] = False
            data["authenticated"] = False
            return data, 401
        else:
            cred = s.oauth2_user.credentials
            cred = json.loads(cred)
            _, token = refresh_g_access_token(cred)
            data["authenticated"] = True
            data["jwt"] = token
            data["guser_id"] = s.oauth2_user.sub
            return data


