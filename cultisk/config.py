import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Auth:
    SCOPE = ["https://www.googleapis.com/auth/userinfo.email", "openid profile",
             'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify',
             "https://www.googleapis.com/auth/userinfo.profile"]
    CLIENT_ID = "***REMOVED***"
    CLIENT_SECRET = "***REMOVED***"
    REDIRECT_URI = "http://127.0.0.1:5000/callback/auth-callback"
    AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI = "https://accounts.google.com/o/oauth2/token"
    USER_INFO = "https://www.googleapis.com/userinfo/v2/me"


class HIBP:
    API_KEY = "***REMOVED***"
    BASE_URL_ACCOUNT = "https://haveibeenpwned.com/api/v3"
    BASE_URL_PASSWORD = "https://api.pwnedpasswords.com/range"


class Config:
    APP_NAME = "Cultisk"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "5791628bb0b13ce0c676dfde280ba245"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    PAGINATE_MAX_SIZE = 20
    PAGINATE_PAGE_SIZE = 10


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test.db")


class ProdConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "prod.db")


config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}
