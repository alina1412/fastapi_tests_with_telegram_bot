
import asyncio
import csv

import aiohttp

from service.schemas import QuestionListRequest
from telegram_service.process import CallHandlersBase, CallHandlersQuizBulk


directory = './extra_data/'
filename = "questions.csv"


async def from_db_to_csv():
        data = QuestionListRequest(active=1)
        questions = await CallHandlersQuizBulk().load_questions(data)
  
        with open(directory + filename, "w", newline='', encoding="utf8") as outfile:
            writer = csv.writer(outfile, delimiter=";")
            writer.writerow(("id", "text", "active", "updated_dt")) # , "answers"
            for row in questions:
                row = list(dict(row).values())
                writer.writerow(row)


if __name__ == "__main__":
    asyncio.run(from_db_to_csv())
