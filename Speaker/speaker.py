from utils import main_thread, notifications_thread, speech
import time
import json
import requests
import threading


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

        if answer.status_code ==200:
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
        playaudiofunction,
        **kwargs
    ):
        """
        kwargs:
            - lock_obj
            - event_obj
            - speech_cls
        """
        self.config = config
        self.playaudiofunction = playaudiofunction

        if 'event_obj' in kwargs:
            self.event_obj = kwargs['event_obj']
        else:
            self.event_obj = threading.Event()

        if 'lock_obj' in kwargs:
            self.lock_obj = kwargs['lock_obj']
        else:
            self.lock_obj = threading.RLock()

        if 'speech_class' in kwargs:
            self.speech_class = kwargs['speech_class']
        else:
            self.speech_cls = speech.Speech(
                config['api_key'],
                config['catalog'],
                playaudiofunction
            )

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
    with open("speaker_config.json", "r") as f:
        config = json.load(f)

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
        speech.playaudiofunction,
        speech_cls = speech_cls
    )
    print("Creating notiofication thread...")
    notifications_thread_cls = notifications_thread.NotificationsAgentThread(
        notifications_thread.notifications_list,
        config, main_thread.raspberryInputFunction, event_obj, speech_cls, lock_obj,
        host=config['domen'],
    )

    print("Creating main thread...")
    main_thread_cls = main_thread.MainThread(
        main_thread.raspberryInputFunction,
        main_thread.activitiesList, config['token'], config['domen'],
        speech_cls, lock_obj)

    print("Running Notification thread")
    notifications_thread_cls.start()

    print("Running main thread")
    main_thread_cls.start()
