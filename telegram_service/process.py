# import asyncio
import json
from random import shuffle
from urllib.parse import urlencode

import aiohttp

from service.schemas import (
    IsCorrectAnsResponse,
    QuestionAddResponse,
    QuestionResponse,
    QuestionInQuizResponse,
    QuizResponse,
    ScoreResponse,
)
from telegram_service.schemas_tg import QuizOutDto
from telegram_service.tg_config import URL_START, logger


class CallHandlersBase:
    async def load_json_post_handler(self, url, data=None):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data=data, headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status not in (200, 201):
                    try:
                        logger.error(await resp.json())
                    except Exception:
                        ...
                    return None
                json_resp = await resp.json()
                logger.info(json_resp)
                return json_resp

    async def load_json_put_handler(self, url, data=None):
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url, data=data, headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status not in (200, 201):
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
                if resp.status not in (200, 204):
                    logger.error(await resp.json())
                    return None
                json_resp = await resp.json()
                logger.info(json_resp)
                return json_resp

    async def load_json_get_handler(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
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
        res = await self.load_json_get_handler(url)
        return res["update_id"] if res else None


class CallHandlersQuizBulk(CallHandlersBase):
    async def load_quiz(self, data: dict | None = None) -> QuizResponse | None:
        url = URL_START + "/v1/show-quiz"
        if not data:
            data = {
                "active": 1,
                "limit": 50,
                "offset": 0,
                "order": "updated_dt",
                "text": "question",
            }

        url = url + "?" + urlencode(data)
        res = await self.load_json_get_handler(url)
        return QuizResponse(**res) if res else None

    async def load_questions(
        self, data: dict | None = None
    ) -> list[QuestionResponse]:
        url = URL_START + "/v1/questions"
        if not data:
            data = {
                "active": 1,
                "limit": 50,
                "offset": 0,
                "order": "updated_dt",
            }
        data_json = json.dumps(data)
        questions = await self.load_json_post_handler(url, data_json)
        if not questions:
            return []
        return [QuestionResponse(**question) for question in questions]


class CallHandlersQuizGame(CallHandlersBase):
    async def get_next_question(self, tg_id: int) -> QuestionResponse | None:
        url = URL_START + "/v1/round-question"
        data = json.dumps({"tg_id": tg_id})
        question = await self.load_json_post_handler(url, data)
        return QuestionResponse(**question) if question else None

    async def next_question_with_ans_opts(
        self, tg_id: int
    ) -> QuestionInQuizResponse | None:
        url = URL_START + "/v1/round-question-id"
        data = json.dumps({"tg_id": tg_id})
        res = await self.load_json_post_handler(url, data)
        if not res:
            logger.info("not next question_id")
            return None
        question_id = res["question_id"]
        data = res  # json.dumps(res)
        questions_dict = await CallHandlersQuizBulk().load_quiz(data)
        if not questions_dict:
            return None
        question = questions_dict.root[question_id]
        shuffle(question.answers)
        return question

    async def transform_to_text_and_btns(
        self, next_question: QuestionInQuizResponse
    ) -> QuizOutDto:
        text = (
            next_question.text
            + "\n"
            + "\n".join(
                [
                    f"{ind}: {ans.text}"
                    for ind, ans in enumerate(next_question.answers, start=1)
                ]
            )
        )
        buttons = [
            [
                {
                    "text": ind,
                    "callback_data": json.dumps(
                        {"question_id": next_question.id, "choice": ans.id}
                    ),
                }
                for ind, ans in enumerate(next_question.answers, start=1)
            ]
        ]
        return QuizOutDto(question=text, buttons=buttons)

    async def edit_score_of_player(self, tg_id: int) -> int:
        url = URL_START + f"/v1/edit-score?tg_id={tg_id}"
        # data = json.dumps({"tg_id": tg_id})
        res_dict = await self.load_json_put_handler(url, "{}")
        return (
            res_dict.get("score", None) if isinstance(res_dict, dict) else None
        )

    async def mark_question_answered(self, question_id: int, tg_id: int):
        url = URL_START + "/v1/mark-answered"
        res_dict = await self.load_json_put_handler(
            url, json.dumps({"tg_id": tg_id, "question_id": question_id})
        )
        return "success" in res_dict

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

    async def register_player_if_new(self, tg_id: int) -> None:
        url = URL_START + "/v1/add-player" + "?tg_id={}".format(tg_id)
        await self.load_json_post_handler(url)

    async def get_score_of_player(self, tg_id: int) -> str:
        url = URL_START + "/v1/player-score" + "?tg_id={}".format(tg_id)
        res = await self.load_json_get_handler(url)
        return (
            f"""your score is {ScoreResponse(**res).score}"""
            if res
            else """can't check score..."""
        )


class CallHandlersAdminFunc(CallHandlersBase):
    async def add_question(self, data: dict):
        """data_example = {
            "active": 1,
            "text": "question"
        }
        """
        url = URL_START + "/v1/add-question"
        data = json.dumps(data)
        res = await self.load_json_post_handler(url, data)
        return QuestionAddResponse(**res) if res else None

    async def edit_question(self, question_dto):
        question_id = question_dto.question_id
        corrected = question_dto.question
        active = question_dto.active
        ans: list[int] = question_dto.ans  # [0]
        url = (
            URL_START
            + "/v1/edit-question"
            + "?id={}&text={}&active={}".format(question_id, corrected, active)
        )
        data = json.dumps(ans)
        return await self.load_json_put_handler(url, data)

    async def add_answer(self, data: dict):
        """data_example = {
            "correct": true,
            "question_id": 1,
            "text": "answer"
        }
        """
        url = URL_START + "/v1/add-answer"
        data = json.dumps(data)
        return await self.load_json_post_handler(url, data)

    async def delete_question(self, q_id):
        url = URL_START + "/v1/delete-question" + "?id={}".format(q_id)
        return await self.load_json_delete_handler(url)

    async def delete_answer(self, ans_id):
        url = URL_START + "/v1/delete-answer" + "?id={}".format(ans_id)
        return await self.load_json_delete_handler(url)


async def get_keyboard():
    pass
