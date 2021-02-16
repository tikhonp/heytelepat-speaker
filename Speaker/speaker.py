from datetime import datetime
import sched
import time
import json
import requests
import threading
from pydub import AudioSegment
from speechkit import speechkit
import speech_recognition as sr
from playsound import playsound


class Speech:
    def __init__(self, config):
        self.filename = config['filename']
        self.filenamev = config['filenamev']

        self.synthesizeAudio = speechkit.synthesizeAudio(
            config['api_key'], config['catalog'])
        self.recognizeShortAudio = speechkit.recognizeShortAudio(
            config['api_key'])
        self.recognizer = sr.Recognizer()

        # self.scheduler = sched.scheduler(time.time, time.sleep)

    def speak(self, text):
        self.synthesizeAudio.synthesize(text, self.filename)

        AudioSegment.from_file(self.filename).export(
            self.filenamev, format="wav")
        speechkit.removefile(self.filename)

        playsound(self.filenamev)
        speechkit.removefile(self.filenamev)


def init():
    with open("speaker_config.json", "r") as f:
        config = json.load(f)

    if config['token'] is None:
        speack_t = threading.Thread(target=speak, args=(
        "Привет! Это колонка Telepat Medsenger. Я помогу тебе следить за своим здоровьем. Сейчас я скажу тебе код из 6 цифр, его надо ввести в окне подключения колонки в medsenger.  Именно так я смогу подключиться.",))
        speack_t.start()
        answer = requests.post(config['domen']+"/speakerapi/init/")
        answer = answer.json()
        config["token"] = answer["token"]
        with open("speaker.config", "w") as f:
            f.write(json.dumps(config))

        speack_t.join()

        speak(
            "Итак, твой код: {}".format(", ".join(list(str(answer["code"])))))

    speech = Speech(config)

    return speech, config


def sayTime():
    now = datetime.now()
    return now.strftime("%A, %-H %-M")


def send_message(speech, config):
    speech.speak("Какое сообщение вы хотите отправить?")

    with sr.Microphone() as source:
        data = speech.recognizer.listen(source)
        data_sound = data.get_raw_data(convert_rate=48000)
        recognize_text = speech.recognizeShortAudio.recognize(data_sound, config['catalog'])
    print(recognize_text)

    answer = requests.post(config['domen']+"/speakerapi/sendmessage/", json={
        'token': config['token'],
        'message': recognize_text,
    })
    if answer.status_code==200:
        speech.speak("Сообщение успешно отправлено!")
    else:
        speech.speak("Произошла ошибка приотправлении сообщения")
        print(answer, answer.text)


if __name__ == "__main__":
    motions = {
        "сообщение": send_message,
    }

    speech, config = init()

    while True:
        input("Press enter and tell something!")

        with sr.Microphone() as source:
            data = speech.recognizer.listen(source)
            data_sound = data.get_raw_data(convert_rate=48000)
            recognize_text = speech.recognizeShortAudio.recognize(data_sound, config['catalog'])
        print(recognize_text)

        if recognize_text.lower() == "хватит":
            break

        for i in motions:
            if i in recognize_text.lower():
                motions[i](speech, config)
