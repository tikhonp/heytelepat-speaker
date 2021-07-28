import json
import logging
import time

import ggwave
import pyaudio
from network import network


def get_ggwave_input():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1,
                    rate=48000, input=True, frames_per_buffer=1024)
    instance = ggwave.init()

    while True:
        data = stream.read(1024, exception_on_overflow=False)
        res = ggwave.decode(instance, data)
        if res is not None:
            try:
                data_str = res.decode('utf-8')
                break
            except ValueError:
                pass

    ggwave.free(instance)
    stream.stop_stream()
    stream.close()
    p.terminate()

    return data_str


def wireless_network_init(object_storage, first=False):
    if first:
        object_storage.speakSpeech.play(
            "Привет! Это колонка Telepat Medsenger. "
            "Для начала работы необходимо подключение к сети. "
            "Для этого сгенерируйте аудиокод с паролем от Wi-Fi.",
            cache=True)
    else:
        object_storage.speakSpeech.play(
            "К сожалению, подключиться не удалось, "
            "Попробуйте сгенерировать код еще раз.", cache=True)

    object_storage.pixels.think()
    data = get_ggwave_input()
    data = json.loads(data)

    n = network.Network(data['ssid'])
    if not n.check_available():
        logging.info("Network is unavailable")
        object_storage.speakSpeech.play(
            "Пока что сеть недоступна, продолжается попытка подключения",
            cache=True)

    object_storage.pixels.think()
    n.create(data['psk'])
    if not n.connect():
        logging.error("Connection error when reconfigure")


def connection_gate(object_storage, systemd=False):
    object_storage.pixels.wakeup()
    first = True
    while not network.check_really_connection():
        if systemd:
            time.sleep(15)
            systemd = False
            continue

        logging.warning("No connection detected")
        wireless_network_init(object_storage, first)
        first = False
        time.sleep(15)

    try:
        object_storage.speech.init_speechkit()
        logging.info("Successfully connected and initialized speechkit")
        if not first:
            object_storage.speakSpeech.play(
                "Подключение к беспроводной сети произошло успешно", cache=True)
    except Exception as e:
        logging.warning(e)
        pass

    else:
        logging.info("Connection exists")
        object_storage.pixels.off()


def cash_phrases(speak_speech):
    data = [
        "Привет! Это колонка Telepat Medsenger. "
        "Для начала работы необходимо подключение к сети. "
        "Для этого сгенерируйте аудиокод с паролем от Wi-Fi.",
        "К сожалению, подключиться не удалось, "
        "Попробуйте сгенерировать код еще раз.",
        "Пока что сеть недоступна, продолжается попытка подключения",
        "Подключение к беспроводной сети произошло успешно"
    ]

    for phrase in data:
        speak_speech.cash_only(phrase)
