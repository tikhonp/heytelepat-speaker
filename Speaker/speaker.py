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
import pickle
from secrets import token_hex


def load_db(filename='data.pickle'):
    """load data from binary database as python object"""

    with open(filename, 'r') as f:
        try:
            data = pickle.load(f)
        except pickle.UnpicklingError:
            return 0

    return data


def write_db(data, filename='data.pickle'):
    """write data as python object to the binary database"""

    with open(filename, 'rb') as f:
        try:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        except pickle.PicklingError:
            return 0


class NotificationsAgent:
    """
    Agent for managering notifications
    It loads from server and save to local data
    with specified user notification settings.
    It creates tametabele agent and sends voice notifications.
    """
    def __init__(
        self,
        token: str,
        host="http://tikhonsystems.ddns.net",
    ):
        self.token = token
        self.host = host
        self.data = load_db()
        if self.data == 0:
            print("ERROR WITH LOADING DATA")
            self.data = self.__get_data__()

            if write_db(self.data) == 0:
                print("ERROR WITH SAVING DATA")

        self.tasks = {}  # All tasks that speaker need to ask for

    def __get_data__(self):
        answer = requests.get(
            self.host+'/speakerapi/tasks/',
            json={"token": self.token},
        )
        if answer.status_code != 200:
            print(
                "ERROR WITH GETTING DATA FROM SERVER!\nStatus code: {}\nAnswer: {}".format(
                    answer.status_code, answer.text))
            return 0

        return answer.json()

    def __add_task__(self, task):
        while True:
            key = token_hex(20)
            try:
                self.data[key]
            except KeyError:
                break

        self.data[key] = task

    def __notifications_loop__(self):
        for i in self.data:
            now = datetime.now()
            if not i['show']:
                continue

            if i['mode'] == 'daily' and now.hour == i['hours']:
                self.__add_task__(i)
            elif i['mode'] == 'monthly' and now.day == i[
                'days_month_day'
            ] and now.hour == i['days_month_hour']:
                self.__add_task__(i)
            elif i['mode'] == 'weekly' and now.weekday() == i[
                'days_week_day'
            ] and i['days_week_hour'] == now.hour:
                self.__add_task__(i)

    def execute_task(self, task_id):
        task = self.data[task_id]







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

    speech = Speech(config)

    if config['token'] is None:
        speack_t = threading.Thread(target=speech.speak, args=(
        "Привет! Это колонка Telepat Medsenger. Я помогу тебе следить за своим здоровьем. Сейчас я скажу тебе код из 6 цифр, его надо ввести в окне подключения колонки в medsenger.  Именно так я смогу подключиться.",))
        speack_t.start()
        answer = requests.post(config['domen']+"/speakerapi/init/")
        answer = answer.json()
        config["token"] = answer["token"]
        with open("speaker.config", "w") as f:
            f.write(json.dumps(config))

        speack_t.join()

        speech.speak(
            "Итак, твой код: {}".format(", ".join(list(str(answer["code"])))))

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
