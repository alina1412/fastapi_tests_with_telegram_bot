import pytest
import requests


add_questions_url = "http://localhost:8000/v1/add-question"

add_answers_url = "http://localhost:8000/v1/add-answer"


data_questions = [
    {
        "text": "question1",
        "active": 1,
    },
    {
        "text": "question2",
        "active": 1,
    },
]

data_answers = [
    {
        "text": "answer 3",
        "correct": True,
        "question_id": 2,
    },
    {
        "text": "answer 4",
        "correct": False,
        "question_id": 2,
    },
]


@pytest.mark.skip()
def test_add_questions():
    for data in data_questions:
        response = requests.post(add_questions_url, json=data)
        assert response.status_code == 201
        print(response.json())


def test_add_answers():
    for data in data_answers:
        response = requests.post(add_answers_url, json=data)
        assert response.status_code == 201
        print(response.json())
