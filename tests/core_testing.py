from sqlalchemy.orm import Session

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
DB_PORT_TESTING = os.getenv("POSTGRES_PORT_TESTING")
DB_NAME_TESTING = os.getenv("POSTGRES_DB_TESTING")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT_TESTING}/{DB_NAME_TESTING}"


@pytest.fixture
def engine_testing():
    engine = create_engine(DATABASE_URL)

    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)

    try:
        yield engine
    finally:
        BaseModel.metadata.drop_all(engine)
        pass


@pytest.fixture
def session_testing(engine_testing):
    with Session(engine_testing) as session:
        yield session
