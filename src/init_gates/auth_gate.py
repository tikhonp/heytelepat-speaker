import json
import logging

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


def update_server_data(object_storage):
    """
    Update server version of speaker and serial number if exists

    :param init_gates.ObjectStorage object_storage: Object Storage instance
    :return: Updated object storage instance
    :rtype: init_gates.ObjectStorage
    """

    answer = requests.get(object_storage.host_http + 'speaker/', json={'token': object_storage.token})
    if answer.status_code == 404:
        logging.error("Token invalid, got 404, resetting token...")
        object_storage.reset_token()
        raise
    answer.raise_for_status()

    update_speaker_data_body = {}
    if (server_version := answer.json().get('version')) != object_storage.version:
        logging.info("Updating server version `{}` -> `{}`".format(server_version, object_storage.version))
        update_speaker_data_body['version'] = object_storage.version

    if (server_serial_no := answer.json().get('serial_no')) != object_storage.serial_no:
        logging.info("Updating server serial no `{}` -> `{}`".format(server_serial_no, object_storage.serial_no))
        update_speaker_data_body['serial_no'] = object_storage.serial_no

    if update_speaker_data_body:
        update_speaker_data_body['token'] = object_storage.token
        answer = requests.put(object_storage.host_http + 'speaker/', json=update_speaker_data_body)
        if not answer.ok:
            logging.error("Error updating speaker data: status code `{}`, text `{}`".format(
                answer.status_code, answer.text[:100]
            ))

    return object_storage


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
        del object_storage.__dict__['token']

    update_server_data(object_storage)

    return object_storage
