from dotenv import load_dotenv
import os

load_dotenv()

SECRET_COOK = os.environ.get("SECRET_COOK")
SECRET_MANAGE = os.environ.get("SECRET_MANAGE")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_NAME = os.environ.get("POSTGRES_NAME")
DB_HOST = os.environ.get("POSTGRES_HOST")
