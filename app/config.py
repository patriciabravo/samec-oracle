import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

USER_DB = os.getenv("USER_DB")
USER_PASSWORD = os.getenv("USER_PASSWORD")
SERVER_DB = os.getenv("SERVER_DB")
NAME_DB = os.getenv("NAME_DB", "XEPDB1")
PORT = os.getenv("PORT")
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = ('Mi App Flask', 'tu_usuario@outlook.com')
FULL_URL_DB = f"oracle+oracledb://{USER_DB}:{USER_PASSWORD}@{SERVER_DB}:{PORT}/?service_name={NAME_DB}"
SECRET_KEY = "supersecret"
UPLOADED_PATH = "uploads"  # carpeta donde se guardarán los archivos
DROPZONE_UPLOAD_MULTIPLE = os.getenv("DROPZONE_UPLOAD_MULTIPLE")
DROPZONE_ALLOWED_FILE_CUSTOM =  os.getenv("DROPZONE_ALLOWED_FILE_CUSTOM")
DROPZONE_ALLOWED_FILE_TYPE =  os.getenv("DROPZONE_ALLOWED_FILE_CUSTOM")
DROPZONE_MAX_FILE_SIZE =  os.getenv("DROPZONE_MAX_FILE_SIZE")  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")  # ../uploads
UPLOAD_FOLDER = os.path.normpath(UPLOAD_FOLDER)

TEMP_FOLDER =UPLOAD_FOLDER + "/temp_fuentes"
FINAL_FOLDER = UPLOAD_FOLDER + "/fuentes"

# Configuración de Flask
class Config:
    SQLALCHEMY_DATABASE_URI = FULL_URL_DB
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = SECRET_KEY
    DROPZONE_UPLOAD_MULTIPLE = DROPZONE_UPLOAD_MULTIPLE
    DROPZONE_ALLOWED_FILE_CUSTOM = DROPZONE_ALLOWED_FILE_CUSTOM
    DROPZONE_ALLOWED_FILE_TYPE = DROPZONE_ALLOWED_FILE_TYPE
    DROPZONE_MAX_FILE_SIZE = DROPZONE_MAX_FILE_SIZE

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

print(Config.SQLALCHEMY_DATABASE_URI)