import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import BaseModel

from dotenv import load_dotenv

load_dotenv(".env")

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME_TESTING = os.getenv("POSTGRES_DB_TESTING")

DATABASE_URL = DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME_TESTING}"
)


engine_testing = create_engine(DATABASE_URL)


@pytest.fixture
def session_testing():
    BaseModel.metadata.create_all(engine_testing)
    with Session(engine_testing) as session:
        try:
            yield session
        finally:
            BaseModel.metadata.drop_all(engine_testing)
