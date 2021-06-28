from telebot import TeleBot
import json
import ggwave
from pydub import AudioSegment
import io


token = "1883863794:AAFy9xuTyU73f6yK70YnZIHkurg403Ddxkg"
bot = TeleBot(token)

data = {}


@bot.message_handler(commands=['start'])
def start(msg):
    user = msg.chat.id
    bot.send_message(user, "Привет. Для подключения колонки нажми /newspeaker")
    data[user] = {}


@bot.message_handler(commands=['newspeaker'])
def newspeaker(msg):
    user = msg.chat.id

    bot.send_message(user, "Пожалуйста введите название сети Wi-Fi (SSID).")

    bot.register_next_step_handler(msg, process_ssid_step)


def process_ssid_step(msg):
    user = msg.chat.id
    data[user]['ssid'] = msg.text
    bot.send_message(user, "Теперь введите пароль от сети.")
    bot.register_next_step_handler(msg, process_pass_step)


def process_pass_step(msg):
    user = msg.chat.id
    data[user]['pass'] = msg.text
    data_str = json.dumps(data[user])

    waveform = ggwave.encode(data_str, txProtocolId=1, volume=20)
    a = AudioSegment(
        waveform,
        sample_width=2,
        frame_rate=48000,
        channels=2
    )
    buf = io.BytesIO()
    a.export(buf, format="ogg")
    buf.seek(0)
    a.export("test.wav", format="wav")
    bot.send_voice(user, buf.getvalue())

bot.polling()
