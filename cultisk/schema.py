from cultisk import ma
from cultisk.Models import Card, Password, Note, OAuth2User, AppSession


# Schemas
class AppSessionSchema(ma.SQLAlchemyAutoSchema):
    oauth2_user = ma.Nested("OAuth2UserSchema", exclude=("app_sessions", "cards", "notes", "passwords"))

    class Meta:
        model = AppSession


class OAuth2UserSchema(ma.SQLAlchemyAutoSchema):
    cards = ma.List(ma.Nested("CardSchema", exclude=("oauth2_user",)), dump_only=True)
    passwords = ma.List(ma.Nested("PasswordSchema", exclude=("oauth2_user",)), dump_only=True)
    notes = ma.List(ma.Nested("NoteSchema", exclude=("oauth2_user",)), dump_only=True)
    app_sessions = ma.List(ma.Nested("AppSessionSchema", exclude=("oauth2_user",)), dump_only=True)

    class Meta:
        model = OAuth2User


class CardSchema(ma.SQLAlchemyAutoSchema):
    uuid = ma.auto_field(dump_only=True)
    oauth2_user = ma.Nested("OAuth2UserSchema", exclude=("app_sessions", "cards", "notes", "passwords"), dump_only=True)

    class Meta:
        model = Card


class PasswordSchema(ma.SQLAlchemyAutoSchema):
    uuid = ma.auto_field(dump_only=True)
    oauth2_user = ma.Nested("OAuth2UserSchema", exclude=("app_sessions", "cards", "notes", "passwords"), dump_only=True)


    class Meta:
        model = Password


class NoteSchema(ma.SQLAlchemyAutoSchema):
    uuid = ma.auto_field(dump_only=True)
    oauth2_user = ma.Nested("OAuth2UserSchema", exclude=("app_sessions", "cards", "notes", "passwords"), dump_only=True)

    class Meta:
        model = Note
