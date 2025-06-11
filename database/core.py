from peewee import PostgresqlDatabase, Model
from dotenv import load_dotenv
import os

load_dotenv(".env")

DB_USER = os.getenv("POSTGRES_USER")
PASSWORD_DB = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")


pg_db = PostgresqlDatabase(
    database=DB_NAME, user=DB_USER, password=PASSWORD_DB, host=DB_HOST, port=DB_PORT
)

pg_db.database


class BaseModel(Model):
    class Meta:
        database = pg_db
