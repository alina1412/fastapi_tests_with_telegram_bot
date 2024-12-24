import json
import os

import aiohttp

from telegram_service.process import (
    CallHandlersQuizGame,
    CallHandlersTg,
)
from telegram_service.schemas_tg import MessageInCallbackDto, MessageInTextDto
from telegram_service.tg_config import logger

token = os.environ.get("TELEGRAM_BOT_API_TOKEN")
assert token


class TgWorkQueue:
    token = token

    async def process(self, message):
        if "callback_query" in message:
            message_dto = MessageInCallbackDto(
                chat_id=message["callback_query"]["message"]["chat"]["id"],
                callback_data=message["callback_query"]["data"],
                # text=message["callback_query"]["message"]["text"]
            )
            await self.process_callback(message_dto)
        else:
            message_dto = MessageInTextDto(
                chat_id=message["message"]["chat"]["id"],
                text_input=message["message"]["text"],
            )
            if message_dto.text_input in ("/start", "/score"):
                await self.process_commands(message_dto)
            elif message_dto.text_input == "test":
                await self.send_test_keyboard(message_dto.chat_id)
            elif message_dto.text_input == "clear":
                await self.send_reply(message_dto.chat_id, "---")

    async def process_commands(self, message: MessageInTextDto):
        text_input = message.text_input
        if text_input == "/start":
            await self.process_command_start(message)
        elif text_input == "/score":
            await self.process_command_score(message)

    async def process_command_start(self, message: MessageInTextDto):
        quiz_manager = CallHandlersQuizGame()
        await quiz_manager.register_player_if_new(message.chat_id)
        await self.send_reply(message.chat_id, "ok")
        await self.next_round(message.chat_id)

    async def process_command_score(self, message: MessageInTextDto):
        quiz_manager = CallHandlersQuizGame()
        score_text = await quiz_manager.get_score_of_player(message.chat_id)
        await self.send_reply(message.chat_id, score_text)

    async def next_round(self, chat_id: int):
        quiz_manager = CallHandlersQuizGame()
        next_question = await quiz_manager.next_question_with_ans_opts(chat_id)
        quiz_out = await quiz_manager.transform_to_text_and_btns(next_question)
        await self.send_reply_keyboard(
            chat_id=chat_id,
            text=quiz_out.question,
            buttons=quiz_out.buttons,
        )

    async def process_callback(self, message: MessageInCallbackDto):
        """User clicked on an inline keyboard button"""
        callback_data = json.loads(message.callback_data)
        question_id = callback_data.get("question_id")
        answer = int(callback_data.get("choice"))
        quiz_manager = CallHandlersQuizGame()
        if question_id:
            iscorrect = await quiz_manager.check_round_answer(
                question_id, ans=[answer]
            )
            text_reply_ans = (
                "correct shall be: "
                + "\n".join(
                    [
                        ans.text
                        for ans in iscorrect.answers
                        if ans.correct is True
                    ]
                )
                if not iscorrect.correct
                else f"correct: {iscorrect.correct}"
            )
            await self.send_reply(message.chat_id, text_reply_ans)
            await quiz_manager.edit_score_of_player(message.chat_id)
            await quiz_manager.mark_question_answered(
                question_id, message.chat_id
            )
            await self.next_round(message.chat_id)

    async def send_test_keyboard(self, chat_id):
        buttons = [
            [
                {
                    "text": str(i),
                    "callback_data": json.dumps(
                        {"question_id": 1, "choice": i}
                    ),
                }
                for i in (1, 2, 3, 4)
            ]
        ]
        text = "question: \n1: aa \n2: bb \n3: cc \n4: dd"
        await self.send_reply_keyboard(
            chat_id=chat_id, text=text, buttons=buttons
        )

    async def send_reply_keyboard(
        self, chat_id: int, text: str, buttons: list[list]
    ):
        keyboard = json.dumps({"inline_keyboard": buttons})
        data = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}
        """keyboard = json.dumps({"keyboard": buttons, 
        "one_time_keyboard": True})
        data = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}"""
        return await self.send_tg_message(data)

    async def send_reply(self, chat_id: int, text: str):
        data = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps({"remove_keyboard": True}),
        }
        return await self.send_tg_message(data)

    async def send_tg_message(self, data: dict):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        async with aiohttp.ClientSession() as client:
            async with client.post(url, data=data) as resp:
                if resp.status != 200:
                    try:
                        err = json.loads(resp.content._buffer[0])["description"]
                        logger.error("tg error %s", err, exc_info=1)
                    except Exception as exc:
                        logger.error("tg error", exc_info=exc)
                        return None
                return resp


class TgPullQueue:
    token = token
    offset = 0

    def __init__(self):
        self.offset = 0

    async def get_tg_updates(self, method_name="getUpdates"):
        """Proceed not files"""
        url = f"https://api.telegram.org/bot{self.token}/{method_name}"
        params = {
            "offset": self.offset,
            "timeout": 30,
            "allowed_updates": [],
            # "message", "inline_query", "callback_query"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data=params, headers={"Content-Type": "application/json"}
            ) as resp:
                json_resp = await resp.json()
                logger.info(json.dumps(json_resp))
                if not json_resp["ok"]:
                    logger.error(
                        "json not ok %s", json.dumps(json_resp), exc_info=1
                    )
                messages = json_resp["result"]
                return messages

    async def get_new_messages(self):
        last_id = await CallHandlersTg().get_last_tg_id()
        self.offset = last_id + 1
        messages = await self.get_tg_updates()

        new_mess = []
        for message in messages:
            if message["update_id"] >= self.offset:
                new_mess.append(message)
                self.offset = messages[-1]["update_id"]
        if new_mess:
            await CallHandlersTg().update_tg_id(messages[-1]["update_id"])
            self.offset = messages[-1]["update_id"] + 1
        return new_mess
