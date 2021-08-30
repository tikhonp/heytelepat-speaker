import logging
import sys
import json

import requests

from init_gates.config_gate import save_config
from init_gates.connection_gate import get_ggwave_input


def init(object_storage):
    """
    Exchange auth code to token

    :param init_gates.ObjectStorage object_storage: Object Storage instance
    :return: Config dictionary
    :rtype: dict
    """
    object_storage.pixels.think()

    answer = requests.get(
        object_storage.host_http + 'speaker/init/', json={'code': object_storage.auth_code}
    )
    answer.raise_for_status()
    answer = answer.json()
    config = object_storage.config
    config['token'] = answer.get('token')
    save_config(config, object_storage.config_filename)

    logging.info("Authentication passed")
    object_storage.play_speech.play(
        "Отлично! Устройство настроено. Чтобы узнать, о моих возможностях, спросите, 'что ты умеешь?'",
        cache=True
    )

    return config


def auth_gate(object_storage):
    """
    Provides getting token if it does not exists

    :param init_gates.ObjectStorage object_storage: Object Storage instance
    :return: Updated object storage instance
    :rtype: init_gates.ObjectStorage
    """
    if not object_storage.token:
        if object_storage.auth_code is None:
            logging.warning("auth code is None")

            object_storage.play_speech.play(
                "Токен не найден. Cгенерируйте и воспроизведите аудиокод.", cache=True
            )
            data = json.loads(get_ggwave_input())
            object_storage.auth_code = data.get('code')

        logging.info("Token does not exist, authentication")
        object_storage.config = init(object_storage)
        del object_storage.token
    else:
        answer = requests.get(object_storage.host_http + 'speaker/', json={'token': object_storage.token})
        answer.raise_for_status()
        if (server_version := answer.json().get('version')) != object_storage.version:
            logging.info("Updating server version `{}` -> `{}`".format(server_version, object_storage.version))
            answer = requests.put(object_storage.host_http + 'speaker/',
                                  json={'token': object_storage.token,
                                        'version': object_storage.version})
            if not answer.ok:
                logging.error(
                    "Error updating version: status code `{}`, text `{}`".format(answer.status_code, answer.text[:100]))

    return object_storage
