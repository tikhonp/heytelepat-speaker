from network import network
import ggwave
import pyaudio
import json
import time
import logging


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
                return data_str
            except ValueError:
                pass

    ggwave.free(instance)

    stream.stop_stream()
    stream.close()

    p.terminate()


def wirless_network_init(objectStorage, first=False):
    if first:
        objectStorage.speakSpeech.play(
            "Привет! Это колонка Telepat Medsenger. "
            "Для начала работы необходимо подключение к сети. "
            "Для этого сгенерируйте аудиокод с паролем от Wi-Fi.",
            cache=True)
    else:
        objectStorage.speakSpeech.play(
            "К сожалению подключиться не удалось, "
            "Попробуйте сгенерировать код еще раз.", cache=True)

    objectStorage.pixels.think()
    data = get_ggwave_input()
    data = json.loads(data)

    n = network.Network(data['ssid'])
    if not n.check_available():
        logging.info("Network is unavailable")
        objectStorage.speakSpeech.play(
            "Пока что сеть недоступна, продолжается попытка подключения",
            cache=True)

    objectStorage.pixels.think()
    n.create(data['psk'])
    if not n.connect():
        logging.error("Connection error when reconfigure")


def ConnectionGate(objectStorage, systemd=False):
    objectStorage.pixels.wakeup()
    first = True
    while not network.check_really_connection():
        if systemd:
            time.sleep(15)
            systemd = False
            continue

        logging.warning("No connection detected")
        wirless_network_init(objectStorage, first)
        first = False
        time.sleep(15)

    try:
        objectStorage.speech.init_speechkit()
        logging.info("Successfully connected and initilized speechkit")
        if not first:
            objectStorage.speakSpeech.play(
                "Подключение к беспроводной сети произошло успешно", cache=True)
    except Exception as e:
        logging.warning(e)
        pass

    else:
        logging.info("Connection exists")
        objectStorage.pixels.off()


def cash_phrases(speakSpeech):
    data = [
        "Привет! Это колонка Telepat Medsenger. "
        "Для начала работы необходимо подключение к сети. "
        "Для этого сгенерируйте аудиокод с паролем от Wi-Fi.",
        "К сожалению подключиться не удалось, "
        "Попробуйте сгенерировать код еще раз.",
        "Пока что сеть недоступна, продолжается попытка подключения",
        "Подключение к беспроводной сети произошло успешно"
    ]

    for phrase in data:
        speakSpeech.cash_only(phrase)
