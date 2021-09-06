import json
import logging
import time

import ggwave
import pyaudio

from network import Network, check_connection_ping


class BasePhrases:
    hello = "Привет! Это колонка Telepat Medsenger."
    need_connection = "Необходимо подключение к сети, если беспроводная сеть Wi-Fi включена сгенерируйте аудиокод"\
                      " в приложении. В случае, если беспроводная сеть не активна, включите ее и переподключите"\
                      " питание заново."
    connection_error = "К сожалению, подключиться не удалось, попробуйте сгенерировать код еще раз."
    network_unavailable = "Пока что сеть недоступна, продолжается попытка подключения."


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
    :return: Integer auth code given from audio
    :rtype: integer | None
    """
    text = BasePhrases.need_connection if first else BasePhrases.connection_error
    object_storage.play_speech.play(text, cache=True)

    object_storage.pixels.think()

    data = json.loads(get_ggwave_input())
    network = Network(data.get('ssid'))

    if not network.available:
        logging.info("Network is unavailable")
        object_storage.play_speech.play(BasePhrases.network_unavailable, cache=True)

    network.create(data.get('psk'))

    if not network.connect():
        logging.error("Connection error when reconfigure")

    time.sleep(5)

    return data.get('code')


def connection_gate(object_storage, check_connection_function=check_connection_ping, check_connection_retries=8):
    """Gate provides internet connection if it does not exist

    :param init_gates.ObjectStorage object_storage: ObjectStorage instance
    :param function check_connection_function: function that provides checking connection,
    default `check_connection_ping`
    :param integer check_connection_retries: Number of reties to call check_connection func
    :return: Integer auth code given from audio
    :rtype: integer | None
    """
    object_storage.pixels.wakeup()
    first = True
    code = None

    while not check_connection_function(object_storage.host):
        logging.info("Network unavailable, connection gate active.")
        for i in range(check_connection_retries):
            if check_connection_function(object_storage.host):
                break
            time.sleep(1)
        else:
            logging.warning("No connection detected")
            code = wireless_network_init(object_storage, first)

        first = False

    if not object_storage.session:
        object_storage.init_speechkit()

    logging.info("Successfully connected and initialized speechkit")

    if not first:
        object_storage.play_speech.play("Подключение к беспроводной сети произошло успешно.", cache=True)
    else:
        logging.info("Connection exists")
        object_storage.pixels.off()

    return code


def cash_phrases(speak_speech):
    attrs = filter(lambda a: not a.startswith('__'), dir(BasePhrases))

    for phrase in attrs:
        speak_speech.cash_only(getattr(BasePhrases, phrase))
