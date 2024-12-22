import asyncio
import json

import aiohttp

from service.schemas import (
    IsCorrectAnsResponse,
    QuestionResponse,
    QuestionResponseInQuiz,
    QuizResponse,
)
from telegram_service.schemas_tg import QuizOutDto
from telegram_service.tg_config import logger, URL_START


class CallHandlersBase:
    async def load_json_post_handler(self, url, data=None):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data=data, headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    logger.error(await resp.json())
                    return None
                json_resp = await resp.json()
                logger.info(json_resp)
                return json_resp

    async def load_json_put_handler(self, url, data=None):
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url, data=data, headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status != 200:
                    logger.error(await resp.json())
                    return None
                json_resp = await resp.json()
                logger.info(json_resp)
                return json_resp

    async def load_json_delete_handler(self, url, kwargs=None):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url,
                # **kwargs,
                headers={"Content-Type": "application/json"},
            ) as resp:
                if resp.status != 200:
                    logger.error(await resp.json())
                    return None
                json_resp = await resp.json()
                logger.info(json_resp)
                return json_resp


class CallHandlersTg(CallHandlersBase):
    async def update_tg_id(self, upd_id):
        data = json.dumps({"update_id": upd_id})
        url = URL_START + "/tg.update"
        return await self.load_json_put_handler(url, data=data)

    async def get_last_tg_id(self):
        url = URL_START + "/tg.get_update_id"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(await resp.json())
                    return None
                res = await resp.json()
                return res["update_id"]


class CallHandlersQuizBulk(CallHandlersBase):
    async def load_quiz(self, data=None):
        url = URL_START + "/v1/show-quiz"
        if not data:
            data = json.dumps(
                {
                    "active": 1,
                    "limit": 50,
                    "offset": 0,
                    "order": "updated_dt",
                    "text": "question",
                }
            )
        res = await self.load_json_post_handler(url, data)
        return QuizResponse(**res)

    async def load_questions(self, data) -> list[QuestionResponse]:
        url = URL_START + "/v1/questions"
        data = """{
            "active": 1,
            "limit": 50,
            "offset": 0,
            "order": "updated_dt"
        }"""
        questions = await self.load_json_post_handler(url, data)
        return [QuestionResponse(**question) for question in questions]


class CallHandlersQuizGame(CallHandlersBase):
    async def get_next_question(self, tg_id: int) -> QuestionResponse:
        url = URL_START + "/v1/round-question"
        data = json.dumps({"tg_id": tg_id})
        question = await self.load_json_post_handler(url, data)
        return QuestionResponse(**question) if question else None

    async def next_question_with_ans_opts(
        self, tg_id: int
    ) -> QuestionResponseInQuiz | None:
        url = URL_START + "/v1/round-question-id"
        data = json.dumps({"tg_id": tg_id})
        res = await self.load_json_post_handler(url, data)
        if not res:
            logger.info("not next question_id")
            return
        question_id = res["question_id"]
        data = json.dumps(res)
        questions_dict = await CallHandlersQuizBulk().load_quiz(data)
        if not questions_dict:
            return
        return questions_dict.root[question_id]

    async def transform_to_text_and_btns(
        self, next_question: QuestionResponseInQuiz
    ) -> QuizOutDto:
        text = (
            next_question.text
            + "\n"
            + "\n".join(
                [f"{ans.id}: {ans.text}" for ans in next_question.answers]
            )
        )
        buttons = [
            [
                {
                    "text": ans.id,
                    "callback_data": json.dumps(
                        {"question_id": next_question.id, "choice": ans.id}
                    ),
                }
                for ans in next_question.answers
            ]
        ]
        return QuizOutDto(question=text, buttons=buttons)

    async def edit_score_of_player(self, tg_id: int):
        url = URL_START + "/v1/edit-score"
        data = json.dumps({"tg_id": tg_id})
        return await self.load_json_put_handler(url, data)

    async def check_round_answer(
        self, question_id: int, ans: int
    ) -> IsCorrectAnsResponse | None:
        url = (
            URL_START
            + "/v1/submit-answer"
            + "?question_id={}".format(question_id)
        )
        ans = json.dumps(ans)
        res = await self.load_json_post_handler(url, data=ans)
        return IsCorrectAnsResponse(**res) if res else None

    async def register_player_if_new(self, tg_id):
        pass

    async def get_score_of_player(self, tg_id):
        return "your score is 10 (template)"


class CallHandlersAdminFunc(CallHandlersBase):
    async def add_question(self, data):
        url = URL_START + "/v1/add-question"
        data = """{
            "active": 1,
            "text": "question"
        }"""
        return await self.load_json_post_handler(url, data)

    async def edit_question(self):
        q_id = 36
        text = "sdwrgv dvw?"
        active = 1
        url = (
            URL_START
            + "/v1/edit-question"
            + "?id={}&text={}&active={}".format(q_id, text, active)
        )
        ans = [0]
        data = json.dumps(ans)
        return await self.load_json_put_handler(url, data)

    async def add_answer(self, data):
        url = URL_START + "/v1/add-answer"
        data = """{
            "correct": true,
            "question_id": 1,
            "text": "answer"
        }"""
        return await self.load_json_post_handler(url, data)

    async def delete_question(self, q_id):
        url = URL_START + "/v1/delete-question" + "?id={}".format(q_id)
        return await self.load_json_delete_handler(url)

    async def delete_answer(self, ans_id):
        url = URL_START + "/v1/delete-answer" + "?id={}".format(ans_id)
        return await self.load_json_delete_handler(url)


async def get_keyboard():
    pass
