import asyncio
import logging
import os
import random
from urllib.parse import urljoin

import aiogram
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(filename="log.log")
    ],
)




API_TOKEN = "1546857864:AAEPBXnsuVVPTJxzrPM8l4g-lQgDLh867T0"


WEBHOOK_HOST = "https://gentle-brook-78003.herokuapp.com/"
WEBHOOK_URL_PATH = '/webhook/' + API_TOKEN
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)

STIKER_SETS = [
    "Gachimuchi_pack",
    "Derpingpack",
    "Beruhmt"
]
bot = aiogram.Bot(token=API_TOKEN)
state_storage = MemoryStorage()
telegram_api_dispatcher = aiogram.Dispatcher(bot=bot, storage=state_storage)


STIKERS = list()


async def get_stikers():
    global STIKERS
    all_stikers = list()
    for set in STIKER_SETS:
        stikers = await bot.get_sticker_set(set)
        stikers = stikers.stickers
        all_stikers.extend(stikers)
    STIKERS = all_stikers


def custom_filter(message: types.Message):
    words = [
        "пидр", "пидор", "навальный", "фем", "левак", "байден", "biden", "gay", "дела", "аним", "оним", "гейм", "транс", "трап"
    ]
    text = message.html_text.lower()
    for word in words:
        if word in text:
            return True
    return False


@telegram_api_dispatcher.message_handler(custom_filter)
async def check(message: types.Message, state: FSMContext):

    stiker = random.choice(STIKERS)
    chat = message.chat

    await bot.send_sticker(
        reply_to_message_id=message.message_id,
        chat_id=chat.id,
        sticker=stiker.file_id
    )
    await state.reset_state()


async def on_startup(app):
    """Simple hook for aiohttp application which manages webhook"""
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await get_stikers()
    asyncio.ensure_future(telegram_api_dispatcher.start_polling())


def create_app():
    app = get_new_configured_app(dispatcher=telegram_api_dispatcher, path=WEBHOOK_URL_PATH)
    app.on_startup.append(on_startup)
    return app


main = create_app()
