import asyncio
import logging
import random

import aiogram
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext


logging.basicConfig(level=logging.INFO)


_API_TOKEN = "1546857864:AAEPBXnsuVVPTJxzrPM8l4g-lQgDLh867T0"
STIKER_SETS = [
    "Gachimuchi_pack",
    "Derpingpack",
    "Beruhmt"
]
_bot = aiogram.Bot(token=_API_TOKEN)
state_storage = MemoryStorage()
telegram_api_dispatcher = aiogram.Dispatcher(bot=_bot, storage=state_storage)


STIKERS = list()


async def get_stikers():
    global STIKERS
    all_stikers = list()
    for set in STIKER_SETS:
        stikers = await _bot.get_sticker_set(set)
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

    await _bot.send_sticker(
        reply_to_message_id=message.message_id,
        chat_id=chat.id,
        sticker=stiker.file_id
    )
    await state.reset_state()


loop = asyncio.get_event_loop()
loop.create_task(get_stikers())
loop.create_task(telegram_api_dispatcher.start_polling())
loop.run_forever()
