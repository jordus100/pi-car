from db import Settings
from repositories.SettingsRepository import SettingsRepository

def save_sftp_settings(sftp):
    for setting in ['host', 'port', 'username', 'password']:
        if sftp[setting] != '':
            SettingsRepository.update(Settings(name=f'sftp_{setting}', value=sftp[setting]))

def get_sftp_settings():
    sftp = {}
    for setting in ['sftp_host', 'sftp_port', 'sftp_username', 'sftp_password']:
        if not SettingsRepository.get_by_name(setting):
            sftp[setting] = ''
        else:
            sftp[setting] = SettingsRepository.get_by_name(setting).value
    return sftp