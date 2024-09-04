from sqlalchemy.ext.asyncio import AsyncSession

from service.db_watchers import AnswerDb, QuestionDb
from service.schemas import (
    QuestionListRequest,
    QuestionRequest,
    AnswerRequest,
    QuestionResponse,
)


class QuestionsManager:
    session = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_question(self, data: QuestionRequest):
        vals = {"text": data.text}
        return await QuestionDb(self.session).add_question(vals)

    async def remove_question(self, id_: int):
        await QuestionDb(self.session).remove_question(id_)

    async def deactivate_question(self, id_: int):
        res = await QuestionDb(self.session).deactivate_question(id_)
        return res[0].id if res else None

    async def find_all_answers(self, q_id: int):
        pass

    async def find_correct_answer(self, q_id: int):
        res = await QuestionDb(self.session).find_correct_answer(q_id)
        return res[0].id if res else None

    async def compare_correct_answer(self, q_id: int, a_id: int):
        res = await QuestionDb(self.session).find_correct_answer(q_id)
        if not res:
            return None
        return res[0].id == a_id

    async def get_question_by_id(self, id_: int):
        res = await QuestionDb(self.session).get_question_by_id(id_)
        return res[0].id if res else None

    async def get_questions(self, data: QuestionListRequest):
        res = await QuestionDb(self.session).get_questions(data)
        # resp = [{"text": u.text, "id": u.id, "active": u.active} for u in res]
        resp = [u.__dict__ for u in res]
        return resp


class AnswersManager:
    session = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_answer(self, data: AnswerRequest):
        vals = data.dict()
        res = await AnswerDb(self.session).add_answer(vals)
        return res  # res[0].id if res else None

    async def remove_answer(self, id_: int):
        await AnswerDb(self.session).remove_answer(id_)

    async def get_answer_by_id(self, ans_id: int):
        res = await AnswerDb(self.session).get_answer_by_id(ans_id)
        return res[0].id if res else None

    async def get_answers_for_question(self, q_id: int):
        res = await AnswerDb(self.session).get_answer_by_id(q_id)
        # data = [{"username": u.username, "id": u.id} for u in res]
        resp = [u.__dict__ for u in res]
        return resp
