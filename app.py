import os
from flask import Flask, request, jsonify, session
from flask.cli import with_appcontext
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint

from db import db
from repositories.UserRepository import UserRepository
import controllers.UserController


def init_app(db, config):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    Migrate(app, db)
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Robot"})
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    return app

config_map = {
    'default': 'config.DefaultConfig',
    'testing': 'config.TestingConfig',
}

env = os.getenv('FLASK_ENV', 'default')
config_class = config_map.get(env)

app = init_app(db, config_class)
app.register_blueprint(controllers.UserController.UserBp, url_prefix='/api')


@app.cli.command('seed_db')
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    admin_pass = os.getenv('DEFAULT_PASSWORD')
    UserRepository.createAdmin(admin_pass)


if __name__ == '__main__':
    app.run(debug=True)