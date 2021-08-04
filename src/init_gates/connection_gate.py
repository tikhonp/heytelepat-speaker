import json
import logging
import time

import ggwave
import pyaudio

from network import Network, check_connection_ping


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
            "Необходимо подключение к сети, для этого сгенерируйте аудиокод с паролем от Wi-Fi.", cache=True
        )
    else:
        object_storage.speakSpeech.play(
            "К сожалению, подключиться не удалось, попробуйте сгенерировать код еще раз.", cache=True
        )

    object_storage.pixels.think()

    data = json.loads(get_ggwave_input())
    n = Network(data.get('ssid'))

    if not n.available:
        logging.info("Network is unavailable")
        object_storage.speakSpeech.play(
            "Пока что сеть недоступна, продолжается попытка подключения.", cache=True
        )

    n.create(data.get('psk'))
    if not n.connect():
        logging.error("Connection error when reconfigure")


def connection_gate(object_storage):
    object_storage.pixels.wakeup()
    first = True
    while not check_connection_ping(object_storage.host):
        logging.info("Network unavailable, connection gate active.")
        for _ in range(3):
            if check_connection_ping(object_storage.host):
                break
            time.sleep(0.5)
        else:
            logging.warning("No connection detected")
            wireless_network_init(object_storage, first)

        first = False

    object_storage.speech.init_speechkit()
    logging.info("Successfully connected and initialized speechkit")

    if not first:
        object_storage.speakSpeech.play(
            "Подключение к беспроводной сети произошло успешно.", cache=True
        )
    else:
        logging.info("Connection exists")
        object_storage.pixels.off()


def cash_phrases(speak_speech):
    data = [
        "Привет! Это колонка Telepat Medsenger.",
        "Необходимо подключение к сети, для этого сгенерируйте аудиокод с паролем от Wi-Fi.",
        "К сожалению, подключиться не удалось, попробуйте сгенерировать код еще раз.",
        "Пока что сеть недоступна, продолжается попытка подключения.",
    ]

    for phrase in data:
        speak_speech.cash_only(phrase)
