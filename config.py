import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables globally

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DefaultConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://admin_user:{os.getenv('DB_PASSWORD')}@localhost:3306/Robot"

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
