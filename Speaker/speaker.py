#!/usr/bin/env python

from utils import main_thread, notifications_thread, speech
import time
import json
import requests
import threading
import argparse


def init(speech_cls):
    synthesizedSpeech = speech_cls.create_speech(
        "Привет! Это колонка Telepat Medsenger. Я помогу тебе следить за своим здоровьем. Сейчас я скажу тебе код из 6 цифр, его надо ввести в окне подключения колонки в medsenger.  Именно так я смогу подключиться.")
    synthesizedSpeech.syntethize()
    speack_t = threading.Thread(target=synthesizedSpeech.play, args=set())
    speack_t.start()

    answer = requests.post(config['domen']+"/speakerapi/init/")
    answer = answer.json()
    print(answer)
    config["token"] = answer["token"]
    with open("speaker_config.json", "w") as f:
        json.dump(config, f)

    speack_t.join()

    synthesizedSpeech = speech_cls.create_speech(
        "Итак, твой код: {}".format(", ".join(list(str(answer["code"])))))
    synthesizedSpeech.syntethize()
    synthesizedSpeech.play()

    while True:
        body = {"token": config["token"]}

        answer = requests.get(
            config["domen"]+"/speakerapi/init/checkauth/", json=body)

        if answer.status_code == 200:
            break

        time.sleep(1)

    synthesizedSpeech = speech_cls.create_speech(
        "Отлично! Устройство настроено.")
    synthesizedSpeech.syntethize()
    synthesizedSpeech.play()

    return config


class ObjectStorage:
    def __init__(
        self,
        config,
        inputFunction,
        cash_filename,
        **kwargs
    ):
        """
        kwargs:
            - lock_obj
            - event_obj
            - speech_cls
            - playaudiofunction
            - speakSpeech_cls
        """
        self.config = config
        self.inputFunction = inputFunction

        if 'playaudiofunction' in kwargs:
            self.playaudiofunction = kwargs['playaudiofunction']
        else:
            self.playaudiofunction = None

        if 'event_obj' in kwargs:
            self.event_obj = kwargs['event_obj']
        else:
            self.event_obj = threading.Event()

        if 'lock_obj' in kwargs:
            self.lock_obj = kwargs['lock_obj']
        else:
            self.lock_obj = threading.RLock()

        if 'speech_cls' in kwargs:
            self.speech = kwargs['speech_cls']
        else:
            if self.playaudiofunction is None:
                raise Exception("You must provide playaudiofunction")
            self.speech = speech.Speech(
                config['api_key'],
                config['catalog'],
                self.playaudiofunction
            )

        if 'speakSpeech_cls' in kwargs:
            self.speakSpeech = kwargs['speakSpeech_cls']
        else:
            self.speakSpeech = speech.SpeakSpeech(
                self.speech, cash_filename)

    @property
    def api_key(self):
        return self.config['api_key']

    @property
    def catalog(self):
        return self.config['catalog']

    @property
    def host(self):
        return self.config['domen']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Speaker for telepat.')
    parser.add_argument("-r", "--reset", help="reset speaker token and init",
                        action="store_true")
    parser.add_argument("-cc", "--cleancash", help="clean cashed speaches",
                        action="store_true")
    parser.add_argument("-rb", "--rpibutton", help="add input function as button pressed",
                        action="store_true")
    args = parser.parse_args()

    with open("speaker_config.json", "r") as f:
        config = json.load(f)
        if args.reset:
            config['token'] = None

    print("Hello there! Tikhon systems inc all rights reserved.")
    print("Loaded config, speech class creating...")

    speech_cls = speech.Speech(
        config['api_key'], config['catalog'], speech.playaudiofunction,)

    if config['token'] is None:
        print("Initialisation started")
        config = init(speech_cls)
    print("Initialisation skiped, token already exist")

    objectStorage = ObjectStorage(
        config,
        main_thread.raspberryInputFunction if args.rpibutton else main_thread.simpleInputFunction,
        'cash.data',
        speech_cls=speech_cls
    )
    if args.cleancash:
        objectStorage.speakSpeech.reset_cash()
    
    print("Creating notiofication thread...")
    notifications_thread_cls = notifications_thread.NotificationsAgentThread(
        objectStorage,
        notifications_thread.notifications_list,
    )

    print("Creating main thread...")
    main_thread_cls = main_thread.MainThread(
        objectStorage,
        main_thread.activitiesList
    )

    print("Running Notification thread")
    notifications_thread_cls.start()

    print("Running main thread")
    main_thread_cls.start()
