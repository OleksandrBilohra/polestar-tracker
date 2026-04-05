from flask import Flask
from .models import db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'change-this-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///polestar_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from .routes import bp
        from .seed import seed_if_empty

        app.register_blueprint(bp)
        db.create_all()
        seed_if_empty()

    return app
