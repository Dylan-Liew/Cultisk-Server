from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from itsdangerous import URLSafeTimedSerializer
from .config import config, Auth
from .Paginate import Pagination

app = Flask(__name__)
app.config.from_object(config['dev'])
app.url_map.strict_slashes = False
url_serializer = URLSafeTimedSerializer(app.secret_key)
db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.after_request
def apply_secure_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


pagination = Pagination(app, db)

api = Api(app, version="1.0", title="Cybernetic", doc="", add_specs=False)

from cultisk.helper import get_google_auth
from cultisk.Models import AppSession
from cultisk.Auth_api import api as auth_api
from cultisk.Callbacks import api as callbacks
from cultisk.PasswordManager_Api import api as password_manager_api

api.add_namespace(auth_api)
api.add_namespace(callbacks)
api.add_namespace(password_manager_api)
