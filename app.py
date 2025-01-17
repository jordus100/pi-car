import os
from flask import Flask, request, jsonify, session
from flask.cli import with_appcontext
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint

from controllers.RobotController import RobotBp
from db import db, Settings
from repositories.SettingsRepository import SettingsRepository
from repositories.UserRepository import UserRepository
from controllers.UserController import UserBp


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
app.register_blueprint(UserBp, url_prefix='/api')
app.register_blueprint(RobotBp, url_prefix='/api')


@app.cli.command('seed_db')
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    admin_pass = os.getenv('DEFAULT_PASSWORD')
    UserRepository.create_admin(admin_pass)
    SettingsRepository.add(Settings(name='maxMotorPower', value='100'))
    SettingsRepository.add(Settings(name='motorTrim', value='100'))
    print('Database seeded.')


if __name__ == '__main__':
    app.run(debug=True)
