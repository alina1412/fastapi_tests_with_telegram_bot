import json
import os

import aiohttp


from telegram_service.process import (
    CallHandlersQuizGame,
    CallHandlersTg,
    get_keyboard,
)
from telegram_service.tg_config import logger
from telegram_service.schemas_tg import MessageInCallbackDto, MessageInTextDto

token = os.environ.get("TELEGRAM_BOT_API_TOKEN")
assert token


class TG_WORK_QUEUE:
    token = token

    async def process(self, message):
        # questions = await load_questions()
        '''question_id = 36
        await CallHandlersQuizGame().check_round_answer(
            question_id, ans=[0]
        )'''

        if "callback_query" in message:
            message_dto = MessageInCallbackDto(
                chat_id=message["callback_query"]["message"]["chat"]["id"],
                callback_data=message["callback_query"]["data"],
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
                await self.send_particular_keyboard("", message_dto.chat_id)
            elif message_dto.text_input == "clear":
                await self.send_reply(message_dto.chat_id, "---")

    async def process_commands(self, message: MessageInTextDto):
        text_input = message["message"]["text"]
        if text_input == "/start":
            await self.process_command_start(message)
        elif text_input == "/score":
            await self.process_command_score(message)

    async def process_command_start(self, message: MessageInTextDto):
        pass

    async def process_command_score(self, message: MessageInTextDto):
        pass

    async def process_callback(self, message: MessageInCallbackDto):
        """User clicked on an inline keyboard button"""
        pass

    async def send_particular_keyboard(self, message, chat_id):
        data1 = json.dumps({"question_id": 1})
        buttons = [
            [
                {"text": "Button 1", "callback_data": '1'},
                {"text": "Button 2", "callback_data": "button2"},
            ],
            # [
            #     {"text": "Button 3", "callback_data": "button3"},
            #     {"text": "Button 4", "callback_data": "button4"},
            # ],
        ]
        await self.send_reply_keyboard(
            chat_id=chat_id, text="vvv", buttons=buttons
        )

    async def send_reply_keyboard(self, chat_id, text, buttons):
        keyboard = json.dumps({"inline_keyboard": buttons})
        data = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}
        '''keyboard = json.dumps({"keyboard": buttons, "one_time_keyboard": True})
        data = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}'''
        return await self.send_tg_message(data)

    async def send_reply(self, chat_id, text):
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


class TG_PULL_QUEUE:
    token = token
    offset = 0

    def __init__(self):
        self.offset = 0

    async def get_tg_updates(self, method_name="getUpdates"):
        """Proceed not files"""
        url = f"https://api.telegram.org/bot{self.token}/{method_name}"
        params = {"offset": self.offset, "timeout": 30, 
                  "allowed_updates": [] # "message", "inline_query", "callback_query"
                  }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data=params, headers={"Content-Type": "application/json"}
            ) as resp:
                json_resp = await resp.json()
                logger.info(json.dumps(json_resp))
                if json_resp["ok"]:
                    messages = json_resp["result"]
                    return messages
                else:
                    logger.error("json not ok")
                

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
