from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from service.config import logger
from service.db_watchers import AnswerDb, QuestionDb
from service.schemas import (
    AnswerInResponse,
    AnswerRequest,
    QuestionEditRequest,
    QuestionListRequest,
    QuestionResponse,
    QuestionResponseInQuiz,
)
from service.db_setup.schemas import AnswerDto, QuestionDto


class QuestionsManager:
    session = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_question(self, data: QuestionEditRequest):
        vals = data.model_dump()
        return await QuestionDb(self.session).add_question(vals)

    async def remove_question(self, id_: int):
        return await QuestionDb(self.session).remove_question(id_)

    async def edit_question_by_id(self, vals: dict):
        id_ = vals.pop("id")
        res = await QuestionDb(self.session).edit_question_by_id(id_, vals)
        return res[0].id if res else None

    async def find_correct_answers(self, question_id: int):
        return await QuestionDb(self.session).find_correct_answers(question_id)

    async def compare_correct_answers(self, params: dict):
        question_id, a_ids = params["question_id"], params["answer_ids"]
        if not a_ids:
            return False
        res = await QuestionDb(self.session).find_correct_answers(question_id)
        if not res:
            return None
        res = [r.id for r in res]
        # print(res, a_ids)
        return sorted(res) == sorted(a_ids)

    async def get_question_by_id(self, id_: int):
        res = await QuestionDb(self.session).get_question_by_id(id_)
        return res[0].id if res else None

    async def get_questions(self, data: QuestionListRequest):
        return await QuestionDb(self.session).get_questions(data)

    def convert_quiz_response(self, res):
        responses = {}
        for question, *answers in res:
            if question.id not in responses:
                responses[question.id] = QuestionResponseInQuiz(
                    text=question.text,
                    id=question.id,
                    active=question.active,
                    answers=[],
                )

            for answer in answers:
                if answer:
                    responses[question.id].answers.append(
                        AnswerInResponse(
                            id=answer.id,
                            text=answer.text,
                            correct=answer.correct,
                        )
                    )
        return responses

    async def get_questions_with_answers(self, data: QuestionListRequest):
        res = await QuestionDb(self.session).get_questions_with_answers(data)
        # resp = [{"text": u.text, "id": u.id, "active": u.active} for u in res]
        responses = self.convert_quiz_response(res)
        # responses = [u.__dict__ for u in res]
        return responses


class AnswersManager:
    session = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_answer(self, data: AnswerRequest):
        vals = data.model_dump()
        try:
            res = await AnswerDb(self.session).add_answer(vals)
        except IntegrityError as err:
            logger.error("error ", exc_info=err)
            raise err
        return res  # res[0].id if res else None

    async def remove_answer(self, id_: int):
        return await AnswerDb(self.session).remove_answer(id_)

    async def get_answer_by_id(self, ans_id: int):
        return await AnswerDb(self.session).get_answer_by_id(ans_id)

    async def get_answers_for_question(self, question_id: int):
        return await AnswerDb(self.session).get_answers_for_question(
            question_id
        )
