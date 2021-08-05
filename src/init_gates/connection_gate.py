import json
import logging
import time

import ggwave
import pyaudio

from network import Network, check_connection_ping


def get_ggwave_input():
    """Listen audio and decode it to string if audio encoding got

    :return: Decoded string
    :rtype: string
    """

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1,
                    rate=48000, input=True, frames_per_buffer=1024)
    instance = ggwave.init()

    try:
        while True:
            data = stream.read(1024, exception_on_overflow=False)
            res = ggwave.decode(instance, data)
            if res is not None:
                logging.debug("ggwave instance: {}".format(instance))
                try:
                    data_str = res.decode('utf-8')
                    break
                except ValueError:
                    logging.debug("Value error when decoding")
                    pass
    finally:
        ggwave.free(instance)
        stream.stop_stream()
        stream.close()
        p.terminate()

    return data_str


def wireless_network_init(object_storage, first=False):
    """Provide network initialization cycle

    :param init_gates.ObjectStorage object_storage: ObjectStorage instance
    :param boolean first: True if it the first iteration of wireless network, default `false`
    :return: Connection success result
    :rtype: boolean
    """

    text = "Необходимо подключение к сети, для этого сгенерируйте аудиокод с паролем от Wi-Fi." if first \
        else "К сожалению, подключиться не удалось, попробуйте сгенерировать код еще раз."
    object_storage.speakSpeech.play(text, cache=True)

    object_storage.pixels.think()

    data = json.loads(get_ggwave_input())
    network = Network(data.get('ssid'))

    if not network.available:
        logging.info("Network is unavailable")
        object_storage.speakSpeech.play("Пока что сеть недоступна, продолжается попытка подключения.", cache=True)

    network.create(data.get('psk'))

    if not (result := network.connect()):
        logging.error("Connection error when reconfigure")
    return result


def connection_gate(object_storage, check_connection_function=check_connection_ping, check_connection_retries=4):
    """Gate provides internet connection if it does not exist

    :param init_gates.ObjectStorage object_storage: ObjectStorage instance
    :param function check_connection_function: function that provides checking connection,
    default `check_connection_ping`
    :param integer check_connection_retries: Number of reties to call check_connection func
    :return: None
    :rtype: None
    """

    object_storage.pixels.wakeup()
    first = True
    while not check_connection_function(object_storage.host):
        logging.info("Network unavailable, connection gate active.")
        for i in range(check_connection_retries):
            if check_connection_function(object_storage.host):
                break
            time.sleep(0.2)
        else:
            logging.warning("No connection detected")
            wireless_network_init(object_storage, first)

        first = False

    object_storage.speech.init_speechkit()
    logging.info("Successfully connected and initialized speechkit")

    if not first:
        object_storage.speakSpeech.play("Подключение к беспроводной сети произошло успешно.", cache=True)
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
