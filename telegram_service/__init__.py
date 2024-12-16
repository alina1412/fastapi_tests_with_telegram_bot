import json
import os

import aiohttp


from telegram_service.process import (
    get_keyboard,
    get_last_tg_id,
    load_questions,
    update_tg_id,
)
from telegram_service.tg_config import logger

token = os.environ.get("TELEGRAM_BOT_API_TOKEN")
assert token


class TG_WORK_QUEUE:
    token = token

    async def process(self, message):
        # questions = await load_questions()

        if "callback_query" in message:
            ...
            """# User clicked on an inline keyboard button
            callback_data = message["callback_query"]["data"]
            chat_id = message["callback_query"]["message"]["chat"]["id"]
            print(f"User pressed button with data: {callback_data} in chat ID: {chat_id}")"""
        else:
            text_input = message["message"]["text"]
            chat_id = message["message"]["chat"]["id"]
            print(text_input)

        await self.send_particular_keyboard(message, chat_id)

    async def send_particular_keyboard(self, message, chat_id):
        buttons = [
            [
                {"text": "Button 1", "callback_data": "button1"},
                {"text": "Button 2", "callback_data": "button2"},
            ],
            [
                {"text": "Button 3", "callback_data": "button3"},
                {"text": "Button 4", "callback_data": "button4"},
            ],
        ]
        await self.send_reply_keyboard(
            chat_id=chat_id, text="vvv", buttons=buttons
        )

    async def send_reply_keyboard(self, chat_id, text, buttons):
        keyboard = json.dumps({"keyboard": buttons, "one_time_keyboard": True})

        data = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        async with aiohttp.ClientSession() as client:
            async with client.post(url, data=data) as resp:
                if resp.status != 200:
                    try:
                        err = json.loads(resp.content._buffer[0])["description"]
                        logger.error("tg error %", err)
                    except Exception as exc:
                        logger.error("tg error")
                        return None
                return resp


class TG_PULL_QUEUE:
    token = token
    offset = 0

    def __init__(self):
        self.offset = 0

    async def get_tg_updates(self, method_name="getUpdates"):
        """proceed not files"""
        url = f"https://api.telegram.org/bot{self.token}/{method_name}"
        params = {"offset": self.offset, "timeout": 30, "allowed_updates": []}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data=params, headers={"Content-Type": "application/json"}
            ) as resp:
                json_resp = await resp.json()
                logger.info(json_resp)
                if json_resp["ok"]:
                    messages = json_resp["result"]
                    return messages

    async def get_new_messages(self):
        last_id = await get_last_tg_id()
        self.offset = last_id + 1
        messages = await self.get_tg_updates()

        new_mess = []
        for message in messages:
            if message["update_id"] >= self.offset:
                new_mess.append(message)
                self.offset = messages[-1]["update_id"]
        if new_mess:
            await update_tg_id(messages[-1]["update_id"])
            self.offset = messages[-1]["update_id"] + 1
        return new_mess
