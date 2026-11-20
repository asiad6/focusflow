
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# These objects are shared by the models and the app.
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    # Set up Flask, the database, migrations, and the app routes.
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models
    from app.routes import main

    app.register_blueprint(main)

    return app
