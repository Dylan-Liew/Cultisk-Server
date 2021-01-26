from flask import request, make_response, jsonify, url_for, session
from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from cultisk import db, app, Auth
from cultisk.helper import openid_required, get_openid_identity, get_google_auth
from cultisk.Models import Password, Card, Note, Entry
from cultisk.schema import PasswordSchema, CardSchema, NoteSchema

api = Namespace("password-manager", description="Auth related")


@api.route("/passwords/")
class Passwords(Resource):

    @openid_required
    def get(self):
        user_identifier = get_openid_identity()
        passwords = Password.query.filter_by(oauth2_user_sub=user_identifier, deleted=False).all()
        password_schema = PasswordSchema(many=True, exclude=["oauth2_user", "password", "favorite", "totp_secret"])
        response_passwords = password_schema.dump(passwords)
        response_obj = {
            "success": True,
            "data": {
                "entries": response_passwords
            }
        }
        return response_obj

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
    def get(self, uuid):
        user_identifier = get_openid_identity()
        password_entry = Password.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        if password_entry is not None:
            password_schema = PasswordSchema(exclude=["oauth2_user"])
            response_password_entry = password_schema.dump(password_entry)
            response_obj = {
                "success": True,
                "data": response_password_entry
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such entry saved"
            }
            return make_response(jsonify(response_obj), 404)

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
            response_obj = {
                "success": True
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Entry saved"
            }
            return make_response(jsonify(response_obj), 404)

    @openid_required
    def delete(self, uuid):
        user_identifier = get_openid_identity()
        password_entry: Password = Password.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        if password_entry is not None:
            password_entry.deleted = True
            db.session.commit()
            response_obj = {
                "success": True,
            }
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
    def get(self):
        user_identifier = get_openid_identity()
        cards = Card.query.filter_by(oauth2_user_sub=user_identifier, deleted=False).all()
        card_schema = CardSchema(many=True, exclude=["oauth2_user", "ccv", "expiry_year", "favorite", "expiry_month"])
        response_cards = card_schema.dump(cards)
        response_obj = {
            "success": True,
            "data": {
                "entries": response_cards
            }
        }
        return response_obj

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
    def get(self, uuid):
        user_identifier = get_openid_identity()
        card_entry = Card.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        if card_entry is not None:
            card_schema = CardSchema(exclude=["oauth2_user"])
            response_card_entry = card_schema.dump(card_entry)
            response_obj = {
                "success": True,
                "data": response_card_entry
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such entry saved"
            }
            return make_response(jsonify(response_obj), 404)

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
            response_obj = {
                "success": True
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Entry saved"
            }
            return make_response(jsonify(response_obj), 404)

    @openid_required
    def delete(self, uuid):
        user_identifier = get_openid_identity()
        card_entry: Card = Card.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        if card_entry is not None:
            card_entry.deleted = True
            db.session.commit()
            response_obj = {
                "success": True,
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Entry saved"
            }
            return make_response(jsonify(response_obj), 404)


@api.route("/notes/")
class Notes(Resource):

    @openid_required
    def get(self):
        user_identifier = get_openid_identity()
        notes = Note.query.filter_by(oauth2_user_sub=user_identifier, deleted=False).all()
        note_schema = NoteSchema(many=True, exclude=["oauth2_user", "content", "favorite"])
        response_notes = note_schema.dump(notes)
        response_obj = {
            "success": True,
            "data": {
                "entries": response_notes
            }
        }
        return response_obj

    @openid_required
    def post(self):
        user_identifier = get_openid_identity()
        note_schema = NoteSchema()
        post_data = request.json
        try:
            post_data = note_schema.load(post_data)
        except ValidationError as e:
            return {"success": False, "error": str(e)}
        n = Note(oauth2_user_sub=user_identifier)
        for x in post_data:
            setattr(n, x, post_data.get(x))
        db.session.add(n)
        db.session.commit()
        response_obj = {
            "success": True
        }
        return response_obj


@api.route("/note/<uuid>/")
class NoteDetail(Resource):

    @openid_required
    def get(self, uuid):
        user_identifier = get_openid_identity()
        note_entry = Note.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        if note_entry is not None:
            note_schema = NoteSchema(exclude=["oauth2_user"])
            response_note_entry = note_schema.dump(note_entry)
            response_obj = {
                "success": True,
                "data": response_note_entry
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such entry saved"
            }
            return make_response(jsonify(response_obj), 404)

    @openid_required
    def put(self, uuid):
        user_identifier = get_openid_identity()
        note_entry = Note.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        note_schema = NoteSchema(exclude=["oauth2_user"])
        post_data = request.json
        try:
            post_data = note_schema.load(post_data, instance=note_entry, partial=True)
        except ValidationError as e:
            return {"success": False, "error": str(e)}
        if note_entry is not None:
            for x in post_data:
                setattr(note_entry, x, post_data.get(x))
            db.session.commit()
            response_obj = {
                "success": True
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Entry saved"
            }
            return make_response(jsonify(response_obj), 404)

    @openid_required
    def delete(self, uuid):
        user_identifier = get_openid_identity()
        note_entry: Note = Note.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier, deleted=False).first()
        if note_entry is not None:
            note_entry.deleted = True
            db.session.commit()
            response_obj = {
                "success": True,
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such Entry saved"
            }
            return make_response(jsonify(response_obj), 404)


@api.route("/deleted/")
class Deleted(Resource):

    @openid_required
    def get(self):
        user_identifier = get_openid_identity()
        notes = Note.query.filter_by(oauth2_user_sub=user_identifier, deleted=True).all()
        cards = Card.query.filter_by(oauth2_user_sub=user_identifier, deleted=True).all()
        passwords = Password.query.filter_by(oauth2_user_sub=user_identifier, deleted=True).all()
        note_schema = NoteSchema(many=True, exclude=["oauth2_user", "content", "favorite"])
        password_schema = PasswordSchema(many=True, exclude=["oauth2_user", "password", "favorite", "totp_secret"])
        card_schema = CardSchema(many=True, exclude=["oauth2_user", "ccv", "expiry_year", "favorite", "expiry_month"])
        response_notes = note_schema.dump(notes)
        response_cards = card_schema.dump(cards)
        response_passwords = password_schema.dump(passwords)
        response_obj = {
            "success": True,
            "data": {
                "notes": response_notes,
                "cards": response_cards,
                "passwords": response_passwords
            }
        }
        return response_obj


@api.route("/deleted/<uuid>/")
class DeletedDetail(Resource):

    @openid_required
    def get(self, uuid):
        user_identifier = get_openid_identity()
        entry: Entry = Entry.query.filter_by(uuid=uuid).first()
        o = None
        schema = None
        if entry.type == "card":
            o = Card
            schema = CardSchema(exclude=["oauth2_user"])
        elif entry.type == "password":
            o = Password
            schema = PasswordSchema(exclude=["oauth2_user"])
        elif entry.type == "note":
            o = Note
            schema = NoteSchema(exclude=["oauth2_user"])
        entry = o.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier).first()
        if entry is not None:
            response_entry = schema.dump(entry)
            response_obj = {
                "success": True,
                "data": response_entry
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such deleted entry"
            }
            return make_response(jsonify(response_obj), 404)

    @openid_required
    def delete(self, uuid):
        user_identifier = get_openid_identity()
        entry: Entry = Entry.query.filter_by(uuid=uuid).first()
        o = None
        if entry.type == "card":
            o = Card
        elif entry.type == "password":
            o = Password
        elif entry.type == "note":
            o = Note
        entry = o.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier).first()
        if entry is not None:
            db.session.delete(entry)
            db.session.commit()
            response_obj = {
                "success": True,
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such deleted entry"
            }
            return make_response(jsonify(response_obj), 404)


@api.route("/deleted/<uuid>/restore/")
class DeletedRestore(Resource):

    @openid_required
    def get(self, uuid):
        user_identifier = get_openid_identity()
        entry: Entry = Entry.query.filter_by(uuid=uuid).first()
        o = None
        if entry.type == "card":
            o = Card
        elif entry.type == "password":
            o = Password
        elif entry.type == "note":
            o = Note
        entry = o.query.filter_by(uuid=uuid, oauth2_user_sub=user_identifier).first()
        if entry is not None:
            entry.deleted = False
            db.session.commit()
            response_obj = {
                "success": True
            }
            return response_obj
        else:
            response_obj = {
                "success": False,
                "message": "No such deleted entry"
            }
            return make_response(jsonify(response_obj), 404)
