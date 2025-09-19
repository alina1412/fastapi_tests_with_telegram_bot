import asyncio
import csv
import json

from service.schemas import QuestionAddResponse, QuestionListRequest
from telegram_service.process import (
    CallHandlersAdminFunc,
    CallHandlersQuizBulk,
)

directory = "./extra_data/"

"""
async def questions_from_db_to_csv():
    filename = "questions.csv"
    data = QuestionListRequest(active=1)
    questions = await CallHandlersQuizBulk().load_questions(data)

    with open(
        directory + filename, "w", newline="", encoding="utf8"
    ) as outfile:
        writer = csv.writer(outfile, delimiter=";")
        writer.writerow(("id", "text", "active"))  # "updated_dt" "answers"
        for row_data in questions:
            row_data = list(dict(row_data).values())
            row_data.pop()
            writer.writerow(row_data)
"""


async def answer_to_db(question_id: int, text, correct):
    data = {
        "text": text,
        "correct": int(correct),
        "question_id": question_id,
    }
    await CallHandlersAdminFunc().add_answer(data)


def get_question_answers_from_csv():
    filename = "questions.csv"
    with open(directory + filename, "r", encoding="utf8") as file:
        file.readline()
        while True:
            row = file.readline()
            if not row:
                break
            row = row.strip().split(";")
            answers = json.loads(row[3])
            question_dict = {"text": row[1], "active": int(row[2])}
            yield question_dict, answers


async def questions_from_csv_to_db():
    for question_dict, answers in get_question_answers_from_csv():
        question_add = await CallHandlersAdminFunc().add_question(
            question_dict
        )
        if question_add and question_add.created:
            question_id = question_add.created
            for i, ans in enumerate(answers):
                await answer_to_db(question_id, text=ans, correct=(i == 0))


"""
async def answers_from_csv_to_db():
    filename = "answers.csv"
    with open(directory + filename, "r", encoding="utf8") as file:
        file.readline()
        while True:
            row = file.readline()
            if not row:
                break
            row = row.strip().split(";")
            # id;text;correct;question_id
            await answer_to_db(question_id=int(row[3]), text=row[1], correct=int(row[2]))
"""


if __name__ == "__main__":
    asyncio.run(questions_from_csv_to_db())
