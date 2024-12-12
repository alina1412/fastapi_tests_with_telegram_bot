import asyncio

import aiohttp

from telegram_service import TG_PULL_QUEUE, TG_WORK_QUEUE


async def telegram_main():
    # await delete_answer()
    tg = TG_PULL_QUEUE()
    wq = TG_WORK_QUEUE()
    while True:
        for message in await tg.get_new_messages():
            await wq.process(message)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print("started...")
        asyncio.run(telegram_main())
    except KeyboardInterrupt:
        print("wait...")
        pass
