import asyncio
import json

import aiohttp

from service.schemas import IsCorrectAnsResponse, QuestionResponse
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
    async def load_quiz(self):
        url = URL_START + "/v1/show-quiz"
        data = """{
            "active": 1,
            "limit": 50,
            "offset": 0,
            "order": "updated_dt",
            "text": "question"
        }"""
        return await self.load_json_post_handler(url, data)

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
        ans = json.dumps([ans])
        res = await self.load_json_post_handler(url, data=ans)
        return IsCorrectAnsResponse(**res) if res else None


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
