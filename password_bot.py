#!/usr/bin/env python

"""
Bot for generating passwords audio code
"""
import io
import json
import logging
import soundfile
from pathlib import Path

import ggwave
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler
)

TOKEN = '1883863794:AAFy9xuTyU73f6yK70YnZIHkurg403Ddxkg'
DATA = {}
SSID, PASS = range(2)
BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    logger.info("User %s connected.", user.first_name)
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! Для генерации аудиокода нажми /generate'
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Для генерации аудиокода нажми /generate')


def generate(update: Update, context: CallbackContext) -> int:
    """Begin conversation, ask for ssid"""

    user = update.message.from_user
    logger.info("User %s started generating.", user.first_name)

    if user.id not in DATA:
        DATA[user.id] = {}
    update.message.reply_text("Введите имя сети (ssid).")
    return SSID


def get_ssid(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("SSID of %s: %s", user.first_name, update.message.text)

    DATA[user.id]['ssid'] = update.message.text
    update.message.reply_text("Введите пароль.")

    return PASS


def generate_audio_file(ssid: str, psk: str, user_name: str) -> io.BytesIO:
    data = json.dumps({'ssid': ssid, 'psk': psk})
    waveform = ggwave.encode(data, txProtocolId=2, volume=20)

    out_data = io.BytesIO()
    data, sample_rate = soundfile.read(
        io.BytesIO(waveform), dtype='float32', channels=1, samplerate=48000, subtype='FLOAT', format='RAW'
    )
    soundfile.write(out_data, data, samplerate=sample_rate, format='WAV')

    return out_data


def get_password(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Password of %s: %s", user.first_name, '*' * len(update.message.text))
    DATA[user.id]['psk'] = update.message.text
    data = generate_audio_file(**DATA[user.id], user_name=user.first_name)

    update.message.reply_document(data, filename='play_me.wav')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Отменено.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Start the bot."""
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('generate', generate)],
        states={
            SSID: [MessageHandler(Filters.text, get_ssid)],
            PASS: [MessageHandler(Filters.text, get_password)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
