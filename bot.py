import aiogram
# import asyncio
# import logging
import os
import random
import translators as ts

from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_webhook

# logging.basicConfig(
#     level=logging.INFO,
#     handlers=[
#         # logging.StreamHandler(),
#         logging.FileHandler(filename="log.log")
#     ],
# )

# LOGGER = logging.getLogger(__file__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
STIKER_SETS = os.getenv("STIKER_SETS").split(', ')
WORDS = os.getenv("WORDS").split(', ')
HOST = "0.0.0.0"
PORT = os.getenv("PORT")
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
WEBHOOK_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com/{BOT_TOKEN}"

STIKERS = list()

bot = aiogram.Bot(token=BOT_TOKEN)
state_storage = MemoryStorage()
telegram_api_dispatcher = aiogram.Dispatcher(bot=bot, storage=state_storage)


def get_with_probability(probability=10):
    return random.randint(0, 100) <= probability


def translate(text: str, target="uk"):
    text = text.replace(' ', '|')

    new_text = ts.translate_html(
        text,
        translator=ts.google,
        to_language=target
    )
    return new_text.replace('|', ' ')


async def get_stikers():
    global STIKERS
    all_stikers = list()
    for set in STIKER_SETS:
        stikers = await bot.get_sticker_set(set)
        stikers = stikers.stickers
        all_stikers.extend(stikers)
    STIKERS = all_stikers


def custom_filter(message: types.Message):
    text = message.html_text.lower()
    for word in WORDS:
        if word in text:
            return True
    return False


@telegram_api_dispatcher.message_handler(custom_filter)
async def send_stikers(message: types.Message, state: FSMContext):

    if not get_with_probability(60):
        return

    stiker = random.choice(STIKERS)
    chat = message.chat

    await bot.send_sticker(
        reply_to_message_id=message.message_id,
        chat_id=chat.id,
        sticker=stiker.file_id
    )
    await state.reset_state()


@telegram_api_dispatcher.message_handler()
async def translate_to_uk(message: types.Message, state: FSMContext):

    if not get_with_probability():
        return

    translated = translate(message.html_text)
    await bot.send_message(
        reply_to_message_id=message.message_id,
        chat_id=message.chat.id,
        text=translated
    )
    await state.reset_state()


async def startup():
    await bot.set_webhook(WEBHOOK_URL)
    await get_stikers()


if __name__ == '__main__':
    start_webhook(
        dispatcher=telegram_api_dispatcher,
        webhook_path=WEBHOOK_URL,
        on_startup=startup,
        skip_updates=True,
        host=HOST,
        port=PORT,
    )
