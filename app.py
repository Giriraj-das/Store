from flask import Flask, session
from flask_restx import Api
from flask_migrate import Migrate
from flask_uploads import configure_uploads

from config import Config
from setup_db import db

from views.admin import admin_ns
from views.forms import photos
from views.store import store_ns


app = Flask(__name__)
app.config.from_object(Config())
app.app_context().push()

db.init_app(app)
Migrate(app, db)

configure_uploads(app, photos)

api = Api(app=app, title='Store')
api.add_namespace(admin_ns)
api.add_namespace(store_ns)


# @app.context_processor
# def utility_processor():
#     count = 0
#     for item in session['cart']:
#         count += item['quantity']
#
#     return dict(count=count)


if __name__ == '__main__':
    app.run()
