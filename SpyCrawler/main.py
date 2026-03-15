import asyncio

from config import CHANNELS
from crawler import TelegramCrawler
from database import init_db


async def main():

    init_db()

    crawler = TelegramCrawler()

    await crawler.start()

    for channel in CHANNELS:

        await crawler.crawl_channel(channel)

    await crawler.close()


if __name__ == "__main__":

    asyncio.run(main())