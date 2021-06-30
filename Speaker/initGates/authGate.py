import requests
import json
import time
import logging


def init(objectStorage):
    objectStorage.speakSpeech.play(
        "Колонка еще не авторизована."
        "Сейчас я скажу тебе код из 6 цифр, "
        "его надо ввести в окне подключения колонки в medsenger. ")

    answer = requests.post(objectStorage.host+'/speakerapi/init/')
    answer = answer.json()

    config = objectStorage.config

    config['token'] = answer['token']
    with open(objectStorage.config_filename, 'w') as f:
        json.dump(config, f)

    objectStorage.speakSpeech.play(
        "Итак, твой код: {}".format(", ".join(list(str(answer["code"])))))

    objectStorage.pixels.think()
    while True:
        body = {"token": config["token"]}

        answer = requests.get(
            config["domen"]+"/speakerapi/init/checkauth/", json=body)

        if answer.status_code == 200:
            break

        time.sleep(1)

    logging.info("Authentication passed")
    objectStorage.speakSpeech.play("Отлично! Устройство настроено.")

    return config


def AuthGate(objectStorage):
    if objectStorage.config['token'] is None:
        logging.info("Token does not exist, authetification")
        objectStorage.config = init(objectStorage)

    return objectStorage
