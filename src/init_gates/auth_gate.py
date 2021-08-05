import asyncio
import json
import logging

import requests
import websockets

from init_gates.config_gate import save_config


async def web_socket_auth(host: str, token: str):
    url = host + 'init/checkauth/'

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({'token': token}))
            msg = await ws.recv()
            return msg
    except websockets.exceptions.ConnectionClosedError:
        return None


def init(object_storage):
    object_storage.speakSpeech.play(
        "Колонка еще не авторизована. "
        "Сейчас я скажу тебе код из 6 цифр, "
        "его надо ввести в окне подключения колонки в medsenger. ",
        cache=True)

    answer = requests.post(object_storage.host_http + 'speaker/',
                           json={'version': object_storage.version})
    answer.raise_for_status()
    answer = answer.json()
    config = object_storage.config
    config['token'] = answer.get('token')
    save_config(config, object_storage.config_filename)

    object_storage.speakSpeech.play(
        "Итак, твой код: {}".format(" - ".join(list(str(answer.get('code'))))))

    object_storage.pixels.think()

    authed = None
    while authed is None:
        authed = asyncio.get_event_loop().run_until_complete(
            web_socket_auth(object_storage.host_ws, config['token']))

    if authed != 'OK':
        raise RuntimeError("Auth confirmation failed, '{}'".format(authed))

    logging.info("Authentication passed")
    object_storage.speakSpeech.play(
        "Отлично! Устройство настроено. Чтобы узнать, о моих возможностях, спросите, 'что ты умеешь?'",
        cache=True
    )

    return config


def auth_gate(object_storage):
    if not object_storage.token:
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
