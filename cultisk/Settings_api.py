import json

from flask import request, make_response, jsonify, url_for
from flask_restx import Namespace, Resource
from cultisk import db, app, Auth
from cultisk.helper import openid_required, get_openid_identity, get_google_auth
from cultisk.Models import OAuth2User, AppSession

api = Namespace("settings", description="Settings related")


@api.route("/sync/")
class SettingsSync(Resource):

    @openid_required
    def post(self):
        user_identifier = get_openid_identity()
        try:
            app_identifier = request.json["app_id"]
            settings = request.json["settings"]
        except KeyError:
            return {"success": False, "message": "invalid request"}, 400

        app_s: AppSession = AppSession.query.filter_by(uuid=app_identifier, active=True,
                                                       oauth2_user_sub=user_identifier)
        if app_s is None:
            return {"success": False, "message": "Unknown/expired session"}
        else:
            app_s.oauth2_user.app_settings = json.loads(settings)
            db.session.commit()
            return {"success": True}


@api.route("/get/")
class SettingsGet(Resource):

    @openid_required
    def get(self):
        user_identifier = get_openid_identity()
        try:
            app_identifier = request.args["app_id"]
        except KeyError:
            return {"success": False, "message": "invalid request"}, 400
        app_s: AppSession = AppSession.query.filter_by(uuid=app_identifier, active=True,
                                                       oauth2_user_sub=user_identifier)
        if app_s is None:
            return {"success": False, "message": "Unknown/expired session"}
        else:
            data = app_s.oauth2_user.app_settings
            return {"success": True, "data": data}
