from utils import main_thread, notifications_thread, speech
import json
import requests
import threading


def init(speech):
    synthesizedSpeech = speech.create_speech(
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

    synthesizedSpeech = speech.create_speech(
        "Итак, твой код: {}".format(", ".join(list(str(answer["code"])))))
    synthesizedSpeech.syntethize()
    synthesizedSpeech.play()

    return config


if __name__ == "__main__":
    with open("speaker_config.json", "r") as f:
        config = json.load(f)

    speech_cls = speech.Speech(
        config['api_key'], config['catalog'], speech.playaudiofunction,)

    if config['token'] is None:
        config = init(speech)

    notifications_thread_cls = notifications_thread.NotificationsAgentThread(
        config, main_thread.inputFunction)

    main_thread_cls = main_thread.MainThread(
        main_thread.inputFunction,
        main_thread.activitiesList, config['token'], config['catalog'])

    notifications_thread_cls.run()
    main_thread_cls.run()
