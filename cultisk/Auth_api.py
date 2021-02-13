import json

from flask import request, make_response, jsonify, url_for, session, redirect
from flask_restx import Namespace, Resource
from cultisk import db, url_serializer, app, Auth
from cultisk.Models import AppSession
from cultisk.helper import refresh_g_access_token, get_google_auth

api = Namespace("auth", description="Auth related")


@api.route("/login/")
class Login(Resource):

    def get(self):
        # Identifier is Electron APP Identifier generated on first start
        # Device name is OS hostname
        # OS version is running OS version
        identifier = request.args.get("app_id")
        device_hostname = request.args.get("hostname")
        os_version = request.args.get("os")
        if identifier is None or device_hostname is None or os_version is None:
            return 400
        else:
            check_dup = AppSession.query.filter_by(uuid=identifier).first()
            if check_dup is None:
                google = get_google_auth()
                auth_url, state = google.authorization_url(Auth.AUTH_URI, access_type='offline', prompt="consent")
                s = AppSession(uuid=identifier, os_version=os_version, device_hostname=device_hostname)
                db.session.add(s)
                db.session.commit()
                session['oauth_state'] = state
                session["app_id"] = identifier
                return redirect(auth_url)
            else:
                return "Please close the window and try again"


@api.route("/refresh-token/")
class RefreshAccessToken(Resource):

    def post(self):
        identifier = request.json["app_id"]
        app_session: AppSession = AppSession.query.filter_by(uuid=identifier, active=True, authenticated=True).first()
        if app_session is not None:
            credentials = app_session.oauth2_user.credentials
            credentials = json.loads(credentials)
            _, token = refresh_g_access_token(credentials)
            return {"success": True, "jwt": token, "authenticated": True}
        else:
            return {"success": False, "authenticated": False}
