import asyncio

import aiohttp

from telegram_service import TG_PULL_QUEUE, TG_WORK_QUEUE


async def telegram_main(tg: TG_PULL_QUEUE, wq: TG_WORK_QUEUE):
    
    while True:
        for message in await tg.get_new_messages():
            await wq.process(message)
            await asyncio.sleep(5)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print("started...")
        tg = TG_PULL_QUEUE()
        wq = TG_WORK_QUEUE()
        asyncio.run(telegram_main(tg, wq))
    except KeyboardInterrupt:
        print("wait...")
        pass
