from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from cultisk import db
from cultisk.helper import openid_required, get_openid_identity
from cultisk.Models import Password, Card, Entry
from cultisk.schema import PasswordSchema, CardSchema

api = Namespace("password-manager", description="Auth related")


@api.route("/passwords/")
class Passwords(Resource):

    @openid_required
    def post(self):
        user_identifier = get_openid_identity()
        password_schema = PasswordSchema()
        post_data = request.json
        try:
            post_data = password_schema.load(post_data, partial=("totp_secret", "url"))
        except ValidationError as e:
            return {"success": False, "error": str(e)}
        p = Password(oauth2_user_sub=user_identifier)
        for x in post_data:
            setattr(p, x, post_data.get(x))
        db.session.add(p)
        db.session.commit()
        response_obj = {
            "success": True
        }
        return response_obj


@api.route("/password/<uuid>/")
class PasswordDetails(Resource):

    @openid_required
    def put(self, uuid):
        user_identifier = get_openid_identity()
        password_entry = Password.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        password_schema = PasswordSchema(exclude=["oauth2_user"])
        post_data = request.json
        try:
            post_data = password_schema.load(post_data, instance=password_entry, partial=True)
        except ValidationError as e:
            return {"success": False, "error": str(e)}
        if password_entry is not None:
            for x in post_data:
                setattr(password_entry, x, post_data.get(x))
            db.session.commit()
            updated_entry = Password.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
            response_obj = {
                "success": True
            }
            if updated_entry is not None:
                response_obj["data"] = password_schema.dumps(updated_entry)
            else:
                delete_entry = Password.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=True).first()
                db.session.delete(delete_entry)
                db.session.commit()
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Entry saved"
            }
            return make_response(jsonify(response_obj), 404)


@api.route("/cards/")
class Cards(Resource):

    @openid_required
    def post(self):
        user_identifier = get_openid_identity()
        card_schema = CardSchema()
        post_data = request.json
        try:
            post_data = card_schema.load(post_data)
        except ValidationError as e:
            return {"success": False, "error": str(e)}
        c = Card(oauth2_user_sub=user_identifier)
        for x in post_data:
            setattr(c, x, post_data.get(x))
        db.session.add(c)
        db.session.commit()
        response_obj = {
            "success": True
        }
        return response_obj


@api.route("/card/<uuid>/")
class CardDetails(Resource):

    @openid_required
    def put(self, uuid):
        user_identifier = get_openid_identity()
        card_entry = Card.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        card_schema = CardSchema(exclude=["oauth2_user"])
        post_data = request.json
        try:
            post_data = card_schema.load(post_data, instance=card_entry, partial=True)
        except ValidationError as e:
            return {"success": False, "error": str(e)}
        if card_entry is not None:
            for x in post_data:
                setattr(card_entry, x, post_data.get(x))
            db.session.commit()
            updated_entry = Card.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
            response_obj = {
                "success": True
            }
            if updated_entry is not None:
                response_obj["data"] = card_schema.dumps(updated_entry)
            else:
                delete_entry = Card.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=True).first()
                db.session.delete(delete_entry)
                db.session.commit()
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Entry saved"
            }
            return make_response(jsonify(response_obj), 404)

@api.route("/data/")
class AllData(Resource):

    @openid_required
    def get(self):
        user_identifier = get_openid_identity()
        passwords = Password.query.filter_by(oauth2_user_sub=user_identifier, deleted=False).all()
        cards = Card.query.filter_by(oauth2_user_sub=user_identifier, deleted=False).all()
        password_schema = PasswordSchema(many=True, exclude=["oauth2_user"])
        card_schema = CardSchema(many=True, exclude=["oauth2_user"])
        response_passwords = password_schema.dump(passwords)
        response_cards = card_schema.dump(cards)
        response_obj = {
            "success": True,
            "data": {
                "passwords": response_passwords,
                "cards": response_cards,
            }
        }
        return response_obj
