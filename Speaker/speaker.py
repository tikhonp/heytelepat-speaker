import json
import requests
import threading
import speech_recognition as sr
from speaker_utils import Speech, NotificationsAgent
from actions import send_message


def init():
    with open("speaker_config.json", "r") as f:
        config = json.load(f)

    speech = Speech(config)

    if config['token'] is None:
        speack_t = threading.Thread(target=speech.speak, args=(
        "Привет! Это колонка Telepat Medsenger. Я помогу тебе следить за своим здоровьем. Сейчас я скажу тебе код из 6 цифр, его надо ввести в окне подключения колонки в medsenger.  Именно так я смогу подключиться.",))
        speack_t.start()
        answer = requests.post(config['domen']+"/speakerapi/init/")
        answer = answer.json()
        print(answer)
        config["token"] = answer["token"]
        with open("speaker_config.json", "w") as f:
            json.dump(config, f)

        speack_t.join()

        speech.speak(
            "Итак, твой код: {}".format(", ".join(list(str(answer["code"])))))

    return speech, config


if __name__ == "__main__":
    motions = {
        "сообщение": send_message,
    }

    speech, config = init()

    notificationsagent = NotificationsAgent(
        config,
        speech
    )

    notifications_t = threading.Thread(target=notificationsagent.main_loop)
    notifications_t.start()

    while True:
        input("Press enter and tell something!")

        with sr.Microphone() as source:
            data = speech.recognizer.listen(source)
            data_sound = data.get_raw_data(convert_rate=48000)
            recognize_text = speech.recognizeShortAudio.recognize(
                data_sound, config['catalog'])
        print(recognize_text)

        if recognize_text.lower() == "хватит":
            notifications_t.terminate()
            break

        for i in motions:
            if i in recognize_text.lower():
                motions[i](speech, config)
