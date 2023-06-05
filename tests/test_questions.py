import pytest
from app import schemas


def test_get_all_questions(client):
    res = client.get('/items/results/')
    assert res.status_code == 200


def test_get_one_question(client, test_question):
    res = client.get(f'/items/{test_question[0].id}')
    question = schemas.QuestionOut(**res.json())
    assert question.id == test_question[0].id


def test_get_one_question_not_exist(client, test_question):
    res = client.get('/items/888')
    assert res.status_code == 404


def test_delete_one_question(client, test_question):
    res = client.delete(f'/items/{test_question[0].id}')
    assert res.status_code == 200


@pytest.mark.parametrize('questions_num', [(1)])
def test_create_question(client, test_question, questions_num):
    res = client.post('/items/', json={"questions_num": questions_num})
    assert res.status_code == 201
    assert res.json() == {"detail": "Questions saved"}
