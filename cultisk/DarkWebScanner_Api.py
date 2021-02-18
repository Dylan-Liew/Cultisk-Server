import hashlib
import os

import requests
from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from cultisk import db, Auth
from cultisk.config import HIBP
from cultisk.helper import openid_required, get_openid_identity
from cultisk.Models import OAuth2User
from cultisk.schema import PasswordSchema, CardSchema

api = Namespace("web-scanner", description="Dark Web scanner")


@api.route("/email/")
class EmailLeaked(Resource):

    @openid_required
    def get(self):
        user_identifier = get_openid_identity()
        headers = {
            "hibp-api-key": HIBP.API_KEY,
            "user-agent": "Cultisk security, School Project"
        }
        params = {
            "truncateResponse": False
        }
        user: OAuth2User = OAuth2User.query.filter_by(sub=user_identifier).first()
        url = f'{HIBP.BASE_URL_ACCOUNT}/breachedaccount/{user.email}'
        r = requests.get(url, headers=headers, params=params)
        response_obj = {
            "success": True,
            "data": {
                "paste": [],
                "breach": [],
            }
        }
        breach_data = []
        paste_data = []
        if r.status_code == 200:
            for x in r.json():
                d = {
                    'Name': x['Name'],
                    'BreachDate': x['BreachDate'],
                    'PwnCount': int(x['PwnCount']),
                    'DataClasses': x['DataClasses']
                }
                breach_data.append(d)
        elif r.status_code != 200 or r.status_code != 404:
            return {
                "success": False
            }
        url = f'{HIBP.BASE_URL_ACCOUNT}/pasteaccount/{user.email}'
        z = requests.get(url, headers=headers, params=params)
        if z.status_code == 200:
            for x in z.json():
                d = {
                    'Source': x['Source'],
                    'EmailCount':int(x['EmailCount']),
                }
                paste_data.append(d)
        elif z.status_code != 200 or z.status_code != 404:
            return {
                "success": False
            }
        response_obj["data"]["breach"] = breach_data
        response_obj["data"]["paste"] = paste_data
        return response_obj


@api.route("/password/<hash>")
class PasswordLeaked(Resource):

    @openid_required
    def get(self, hash):
        headers = {
            "hibp-api-key": HIBP.API_KEY,
            "user-agent": "Cultisk security, School Project"
        }
        url = f'{HIBP.BASE_URL_PASSWORD}/{hash}'
        r = requests.get(url, headers=headers)
        text = r.text.replace("\r\n", '|')
        response_obj = {
            "success": True,
            "data": text
        }
        return response_obj
