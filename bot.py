import aiogram
import os
import random

import httpx
import translators as ts

from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_webhook
from aiogram.types import ContentType


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


async def get_anek(url: str = "http://rzhunemogu.ru/RandJSON.aspx?CType=1"):
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        res = res.text[12:-2]  # This API is returning bad JSON
        return res


async def get_stikers():
    global STIKERS
    all_stikers = list()
    for set in STIKER_SETS:
        stikers = await bot.get_sticker_set(set)
        stikers = stikers.stickers
        all_stikers.extend(stikers)
    STIKERS = all_stikers


async def get_random_sticker(sticker_set: str):
    stickers = await bot.get_sticker_set(sticker_set)
    stickers = stickers.stickers
    sticker = random.choice(stickers)
    return sticker.file_id


def custom_filter(message: types.Message):
    text = message.html_text.lower()
    for word in WORDS:
        if word in text:
            return True
    return False


@telegram_api_dispatcher.message_handler(custom_filter)
async def send_stikers(message: types.Message, state: FSMContext):
    global STICKER_COUNTER
    STICKER_COUNTER = 0
    if not get_with_probability(20):
        return

    stiker = random.choice(STIKERS)
    chat = message.chat

    await bot.send_sticker(
        reply_to_message_id=message.message_id,
        chat_id=chat.id,
        sticker=stiker.file_id
    )
    await state.reset_state()

STICKER_COUNTER = 0


@telegram_api_dispatcher.message_handler(content_types=ContentType.STICKER)
async def sticker_observer(message: types.Message, state: FSMContext):
    answers = ["Сраные стикеры", "Зачем буквы изобретали?", "Налепи себе на одно место стикер"]

    global STICKER_COUNTER
    if STICKER_COUNTER < 2:
        STICKER_COUNTER += 1
        return
    if get_with_probability(80):
        await bot.send_message(text=random.choice(answers), chat_id=message.chat.id)
        STICKER_COUNTER = 0
        return


@telegram_api_dispatcher.message_handler()
async def general_jokes(message: types.Message, state: FSMContext):
    global STICKER_COUNTER
    STICKER_COUNTER = 0

    if get_with_probability(1):
        #  Send joke
        anek = await get_anek()
        await bot.send_message(
            text=f"Свежий анек для тебя, дружище :\n\n {anek}",
            chat_id=message.chat.id,
            reply_to_message_id=message.message_id,
        )
        await bot.send_sticker(
            sticker=await get_random_sticker("honka_animated"),
            chat_id=message.chat.id
        )
        return

    if get_with_probability(1):
        # Translate to UK
        translated = translate(message.html_text)
        await bot.send_message(
            reply_to_message_id=message.message_id,
            chat_id=message.chat.id,
            text=translated
        )
    await state.reset_state()


async def startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    await get_stikers()


if __name__ == '__main__':
    start_webhook(
        dispatcher=telegram_api_dispatcher,
        webhook_path=f"/{BOT_TOKEN}",
        on_startup=startup,
        skip_updates=True,
        host=HOST,
        port=PORT
    )
