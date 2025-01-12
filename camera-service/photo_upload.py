import os
import pymysql
import paramiko
from zipfile import ZipFile
from datetime import datetime

from flask.cli import load_dotenv

load_dotenv()
PHOTO_DIR = os.getenv("PHOTO_SAVE_DIR")
ZIP_DIR = "photos_zipped"
DB_CONFIG = {
    "host": "localhost",
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database": "Robot"
}

def get_sftp_credentials():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            query = "SELECT value FROM settings WHERE name = %s"
            cursor.execute(query, ("sftp_host",))
            host = cursor.fetchone()[0]

            cursor.execute(query, ("sftp_port",))
            port = int(cursor.fetchone()[0])

            cursor.execute(query, ("sftp_username",))
            username = cursor.fetchone()[0]

            cursor.execute(query, ("sftp_password",))
            password = cursor.fetchone()[0]

            return host, port, username, password
    finally:
        connection.close()

def zip_photos():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(ZIP_DIR, f"photos_{timestamp}.zip")
    with ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(PHOTO_DIR):
            file_path = os.path.join(PHOTO_DIR, file)
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname=file)
                os.remove(file_path)  # Remove after archiving
    return zip_path

def upload_to_sftp(zip_path, sftp_credentials):
    host, port, username, password = sftp_credentials
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        remote_path = f"{os.path.basename(zip_path)}"
        sftp.put(zip_path, remote_path)
        print(f"Uploaded: {zip_path} to {remote_path}")
    finally:
        sftp.close()
        transport.close()

def main():
    sftp_credentials = get_sftp_credentials()
    zip_path = zip_photos()
    upload_to_sftp(zip_path, sftp_credentials)

if __name__ == "__main__":
    if not os.path.exists(ZIP_DIR):
        os.makedirs(ZIP_DIR)
    main()