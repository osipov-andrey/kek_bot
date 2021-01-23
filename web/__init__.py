import asyncio
import logging
import random
from urllib.parse import urljoin

import aiogram
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.webhook import get_new_configured_app
import translators as ts
from aiohttp import web


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        # logging.FileHandler(filename="log.log"),
        logging.StreamHandler()
    ],
)

LOGGER = logging.getLogger(__file__)

API_TOKEN = "1546857864:AAEPBXnsuVVPTJxzrPM8l4g-lQgDLh867T0"


# WEBHOOK_HOST = "https://gentle-brook-78003.herokuapp.com/"
# WEBHOOK_URL_PATH = '/webhook/' + API_TOKEN
# WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)

STIKER_SETS = [
    "Gachimuchi_pack",
    "Derpingpack",
    "Beruhmt"
]
bot = aiogram.Bot(token=API_TOKEN)
state_storage = MemoryStorage()
telegram_api_dispatcher = aiogram.Dispatcher(bot=bot, storage=state_storage)


STIKERS = list()


def get_with_probability(probability=10):
    return random.randint(0, 100) <= probability


def translate(text, target="uk"):
    try:
        new_text = ts.translate_html(
            text,
            translator=ts.bing,
            to_language=target
        )
        return new_text
    except Exception:
        LOGGER.error("ERROR", exc_info=True)
        return text


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
        "пидр", "пидор", "навальный", "фем", "левак", "байден", "biden",
        "gay", "дела", "аним", "оним", "гейм", "транс", "трап", "день настал", "блокир"
    ]
    text = message.html_text.lower()
    for word in words:
        if word in text:
            return True
    return False


@telegram_api_dispatcher.message_handler(custom_filter)
async def send_stikers(message: types.Message, state: FSMContext):

    if not get_with_probability(50):
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


async def on_startup(app):
    # await bot.delete_webhook()
    # await bot.set_webhook(WEBHOOK_URL)
    await get_stikers()
    asyncio.ensure_future(telegram_api_dispatcher.start_polling())


# def create_app():
#     app = get_new_configured_app(dispatcher=telegram_api_dispatcher, path=WEBHOOK_URL_PATH)
#     app.on_startup.append(on_startup)
#     return app

def create_app():
    app = web.Application()
    # app = get_new_configured_app(dispatcher=telegram_api_dispatcher, path=WEBHOOK_URL_PATH)
    app.on_startup.append(on_startup)
    return app


main = create_app()

# loop = asyncio.get_event_loop()
# loop.create_task(get_stikers())
# loop.create_task(telegram_api_dispatcher.start_polling())
# loop.run_forever()
