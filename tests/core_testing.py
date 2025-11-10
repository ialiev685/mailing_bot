from sqlalchemy.orm import Session
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from config import init_env_file
from database.models import BaseModel

init_env_file()

POSTGRES_HOST_TESTING = os.getenv("POSTGRES_HOST_TESTING", "localhost")

# Так запуска app в образке docker, обращение идет через внутренний port (внешний:внутренний)
PORT = 5435 if POSTGRES_HOST_TESTING == "localhost" else 5432
DATABASE_URL = f"postgresql://test:test@{POSTGRES_HOST_TESTING}:{PORT}/test"


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
