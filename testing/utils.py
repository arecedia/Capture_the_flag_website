import pytest
from sqlmodel import SQLModel, Session, create_engine
from webapp.users.models import user_models
from fastapi.testclient import TestClient
from unittest.mock import patch


def create_db(session):
    from sqlmodel import SQLModel, create_engine, Session

    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    connect_args = {"check_same_thread": False}

    engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    return