import click
from werkzeug.security import generate_password_hash

from db import db, User

class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def save(user):
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def update(user):
        db.session.merge(user)
        db.session.commit()

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def create_admin(password):
        if not User.query.filter_by(is_admin=True).first():
            hash = generate_password_hash(password)
            admin = User(username='admin', password=hash, is_admin=True)
            db.session.add(admin)
            db.session.commit()
            click.echo('Default admin account created.')
        else:
            click.echo('Admin account already exists.')