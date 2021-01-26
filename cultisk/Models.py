from cultisk import db
import uuid


class OAuth2User(db.Model):
    __tablename__ = "oauth2_user"
    sub = db.Column(db.String(100), nullable=True, unique=True, primary_key=True)
    email = db.Column(db.String(100), nullable=True)
    credentials = db.Column(db.Text)
    token = db.Column(db.Text, default=None)
    app_sessions = db.relationship("AppSession", back_populates="oauth2_user")
    passwords = db.relationship("Password", back_populates="oauth2_user")
    notes = db.relationship("Note", back_populates="oauth2_user")
    cards = db.relationship("Card", back_populates="oauth2_user")


class AppSession(db.Model):
    __tablename__ = "app_session"
    uuid = db.Column(db.String(36), unique=True, nullable=False, primary_key=True)
    oauth2_user_sub = db.Column(db.String(30), db.ForeignKey("oauth2_user.sub"), primary_key=True)
    oauth2_user = db.relationship("OAuth2User", back_populates="app_sessions")
    active = db.Column(db.Boolean, default=True)
    os_version = db.Column(db.String(50), nullable=False)
    device_hostname = db.Column(db.Text, nullable=False)


class Entry(db.Model):
    __tablename__ = "entry"

    uuid = db.Column(db.String(36), primary_key=True)
    type = db.Column(db.Text)
    favorite = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'entry',
        'polymorphic_on': type
    }

    def __init__(self, unique_id, type):
        self.type = type
        self.uuid = unique_id


class Password(Entry):
    __tablename__ = 'password'

    uuid = db.Column(db.String(36), db.ForeignKey('entry.uuid'), primary_key=True)
    oauth2_user_sub = db.Column(db.String(30), db.ForeignKey("oauth2_user.sub"), primary_key=True)
    oauth2_user = db.relationship("OAuth2User", back_populates="passwords")
    username = db.Column(db.Text)
    password = db.Column(db.Text)
    totp_secret = db.Column(db.Text, nullable=True, default=None)
    url = db.Column(db.Text, nullable=True, default=None)

    __mapper_args__ = {
        'polymorphic_identity': 'password',
    }

    def __init__(self, oauth2_user_sub, username=None, password=None, totp_secret=None, url=None):
        unique_id = str(uuid.uuid4())
        super(Password, self).__init__(unique_id, "password")
        self.oauth2_user_sub = oauth2_user_sub
        self.uuid = unique_id
        self.username = username
        self.password = password
        self.totp_secret = totp_secret
        self.url = url


class Note(Entry):
    __tablename__ = 'note'

    uuid = db.Column(db.String(36), db.ForeignKey('entry.uuid'), primary_key=True)
    name = db.Column(db.Text)
    oauth2_user_sub = db.Column(db.String(30), db.ForeignKey("oauth2_user.sub"), primary_key=True)
    oauth2_user = db.relationship("OAuth2User", back_populates="notes")
    content = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': 'note',
    }

    def __init__(self, oauth2_user_sub, name=None, content=None):
        unique_id = str(uuid.uuid4())
        super(Note, self).__init__(unique_id, "note")
        self.oauth2_user_sub = oauth2_user_sub
        self.uuid = unique_id
        self.name = name
        self.content = content


class Card(Entry):
    __tablename__ = 'card'

    uuid = db.Column(db.String(36), db.ForeignKey('entry.uuid'), primary_key=True)
    name = db.Column(db.Text)
    brand = db.Column(db.Text)
    oauth2_user_sub = db.Column(db.String(30), db.ForeignKey("oauth2_user.sub"), primary_key=True)
    oauth2_user = db.relationship("OAuth2User", back_populates="cards")
    number = db.Column(db.Text)
    ccv = db.Column(db.Text)
    expiry_month = db.Column(db.Text)
    expiry_year = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': 'card',
    }

    def __init__(self, oauth2_user_sub, name=None, brand=None, number=None, ccv=None, expiry_month=None, expiry_year=None):
        unique_id = str(uuid.uuid4())
        super(Card, self).__init__(unique_id, "card")
        self.oauth2_user_sub = oauth2_user_sub
        self.name = name
        self.brand = brand
        self.uuid = unique_id
        self.number = number
        self.ccv = ccv
        self.expiry_year = expiry_year
        self.expiry_month = expiry_month
