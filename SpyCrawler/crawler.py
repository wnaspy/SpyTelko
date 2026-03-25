import os
import re
import asyncio

from telethon import TelegramClient
from tqdm import tqdm

from config import (
    API_ID,
    API_HASH,
    SESSION_NAME,
    BASE_DOWNLOAD_PATH
)

from database import (
    get_last_message_id,
    update_last_message_id,
    insert_news,
    insert_document
)

url_pattern = re.compile(r"https?://\S+")


def extract_urls(text):
    if not text:
        return []
    return url_pattern.findall(text)


def normalize_filename(name):
    if not name:
        return "unknown_file"
    return name.replace("_", " ")


class TelegramCrawler:

    def __init__(self):

        self.client = TelegramClient(
            SESSION_NAME,
            API_ID,
            API_HASH
        )

        self.download_path = os.path.join(BASE_DOWNLOAD_PATH, "documents")
        os.makedirs(self.download_path, exist_ok=True)

        self.semaphore = asyncio.Semaphore(5)

    async def start(self):
        await self.client.start()

    async def download_file(self, message, channel):
        async with self.semaphore:
            try:
                print(message.file.name)

                file_path = await message.download_media(
                    file=self.download_path
                )

                if file_path:
                    file_name = os.path.basename(file_path)
                    file_name = normalize_filename(file_name)

                    insert_document(
                        channel,
                        message.id,
                        file_name,
                        file_path
                    )

                update_last_message_id(channel, message.id)

            except Exception as e:
                print(f"Error at message {message.id}: {e}")

    async def crawl_channel(self, channel):

        print(f"\nCrawling: {channel}")

        last_id = get_last_message_id(channel)

        latest = await self.client.get_messages(channel, limit=1)

        if not latest:
            print("No messages")
            return

        latest_id = latest[0].id
        total = max(latest_id - last_id, 0)

        if total == 0:
            print("No new messages")
            return

        progress = tqdm(total=total, desc=channel, unit="msg")

        tasks = []

        async for message in self.client.iter_messages(
            channel,
            min_id=last_id,
            reverse=True
        ):
            try:
                text = message.text or ""
                urls = extract_urls(text)

                if message.photo and urls:
                    insert_news(
                        channel,
                        message.id,
                        text,
                        ",".join(urls)
                    )
                    update_last_message_id(channel, message.id)

                elif message.file:
                    tasks.append(self.download_file(message, channel))
                    progress.update(1)
                    continue  

                else:
                    insert_news(
                        channel,
                        message.id,
                        text,
                        ",".join(urls)
                    )
                    update_last_message_id(channel, message.id)

                progress.update(1)

            except Exception as e:
                print(f"Error at message {message.id}: {e}")

        if tasks:
            await asyncio.gather(*tasks)

        progress.close()
        print(f"Finished {channel}")

    async def close(self):
        await self.client.disconnect()
