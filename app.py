from flask import Flask, session, render_template
from flask_restx import Api
from flask_migrate import Migrate
from flask_uploads import configure_uploads

from config import Config
from dao.model.models import Product
from setup_db import db

from views.admin import admin_ns
from views.forms import photos
from views.store import store_ns


def create_app(config: Config) -> Flask:
    """Create main object app"""
    app = Flask(__name__)
    app.config.from_object(config)
    app.app_context().push()

    @app.route('/')
    def index():
        products = db.session.query(Product).all()
        return render_template('index.html', products=products), 200

    api = Api(app=app, title='Store', doc='/docs')
    api.add_namespace(admin_ns)
    api.add_namespace(store_ns)

    db.init_app(app)
    Migrate(app, db)

    configure_uploads(app, photos)

    @app.context_processor
    def utility_processor():
        count = 0
        if session.get('cart'):
            for item in session['cart']:
                count += item['quantity']

        return dict(count=count)

    return app


if __name__ == '__main__':
    application = create_app(Config())
    application.run()
