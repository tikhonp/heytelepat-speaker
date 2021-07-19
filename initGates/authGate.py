import requests
import json
import logging
import websockets
import asyncio


async def webSocketAuth(domen: str, token: str):
    url = 'ws://{}/ws/speakerapi/init/checkauth/'.format(
        domen.split('/')[2])

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({"token": token}))
            msg = await ws.recv()
            return msg
    except websockets.exceptions.ConnectionClosedError:
        return None


def init(objectStorage):
    objectStorage.speakSpeech.play(
        "Колонка еще не авторизована. "
        "Сейчас я скажу тебе код из 6 цифр, "
        "его надо ввести в окне подключения колонки в medsenger. ",
        cashed=True)

    answer = requests.post(objectStorage.host+'/speakerapi/init/')
    answer = answer.json()

    config = objectStorage.config

    config['token'] = answer['token']
    with open(objectStorage.config_filename, 'w') as f:
        json.dump(config, f)

    objectStorage.speakSpeech.play(
        "Итак, твой код: {}".format(", ".join(list(str(answer["code"])))))

    objectStorage.pixels.think()

    authed = None
    while authed is None:
        authed = asyncio.get_event_loop().run_until_complete(
            webSocketAuth(config['domen'], config['token']))

    if authed != 'OK':
        raise RuntimeError("Auth confirmation failed, '{}'".format(authed))

    logging.info("Authentication passed")
    objectStorage.speakSpeech.play(
        "Отлично! Устройство настроено.", cashed=True)

    return config


def AuthGate(objectStorage):
    if objectStorage.config['token'] is None:
        logging.info("Token does not exist, authetification")
        objectStorage.config = init(objectStorage)

    return objectStorage
