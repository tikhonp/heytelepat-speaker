import requests
import json
import logging
import websockets
import asyncio


async def web_socket_auth(domain: str, token: str):
    url = 'ws://{}/ws/speakerapi/init/checkauth/'.format(
        domain.split('/')[2])

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({"token": token}))
            msg = await ws.recv()
            return msg
    except websockets.exceptions.ConnectionClosedError:
        return None


def init(object_storage):
    object_storage.speakSpeech.play(
        "Колонка еще не авторизована. "
        "Сейчас я скажу тебе код из 6 цифр, "
        "его надо ввести в окне подключения колонки в medsenger. ",
        cashed=True)

    answer = requests.post(object_storage.host + '/speakerapi/init/')
    answer = answer.json()

    config = object_storage.config

    config['token'] = answer['token']
    with open(object_storage.config_filename, 'w') as f:
        json.dump(config, f)

    object_storage.speakSpeech.play(
        "Итак, твой код: {}".format(" - ".join(list(str(answer["code"])))))

    object_storage.pixels.think()

    authed = None
    while authed is None:
        authed = asyncio.get_event_loop().run_until_complete(
            web_socket_auth(config['domen'], config['token']))

    if authed != 'OK':
        raise RuntimeError("Auth confirmation failed, '{}'".format(authed))

    logging.info("Authentication passed")
    object_storage.speakSpeech.play(
        "Отлично! Устройство настроено.", cashed=True)

    return config


def auth_gate(object_storage):
    if object_storage.config['token'] is None:
        logging.info("Token does not exist, authentication")
        object_storage.config = init(object_storage)

    return object_storage
