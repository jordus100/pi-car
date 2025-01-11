from db import db, Settings

class SettingsRepository:
    @staticmethod
    def get_all():
        return Settings.query.all()

    @staticmethod
    def get_by_name(name):
        return Settings.query.get(name)

    @staticmethod
    def add(setting):
        db.session.add(setting)
        db.session.commit()

    @staticmethod
    def update(setting):
        db.session.merge(setting)
        db.session.commit()