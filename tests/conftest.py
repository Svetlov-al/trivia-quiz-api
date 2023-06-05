from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app import models
from app.config import settings
from app.database import get_db, Base
import pytest


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:iyu1vap8@localhost:5432/postgres"
# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Testing_SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Testing_SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_question(session):
    question_data = [{
        "question_text": "first question",
        "answer_text": "first answer",
        "created_at": '2022-12-30 22:50:19.727+04'
    }, {
        "question_text": "second question",
        "answer_text": "second answer",
        "created_at": '2022-12-30 22:50:19.727+04'
    }]

    def create_question_model(post):
        return models.QuizQuestion(**post)

    question_map = map(create_question_model, question_data)

    questions = list(question_map)
    session.add_all(questions)
    session.commit()

    questions = session.query(models.QuizQuestion).all()
    return questions
