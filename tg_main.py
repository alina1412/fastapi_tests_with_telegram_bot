import asyncio

from telegram_service import TgPullQueue, TgWorkQueue


async def telegram_main(tg: TgPullQueue, wq: TgWorkQueue):
    while True:
        for message in await tg.get_new_messages():
            await wq.process(message)
        await asyncio.sleep(5)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print("started...")
        tg = TgPullQueue()
        wq = TgWorkQueue()
        asyncio.run(telegram_main(tg, wq))
    except KeyboardInterrupt:
        print("wait...")
        pass
