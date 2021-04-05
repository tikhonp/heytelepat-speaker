from pydub import AudioSegment
from speechkit import speechkit
import speech_recognition as sr
from playsound import playsound
import pickle
from secrets import token_hex
import requests
from datetime import datetime
import time
import json
import dateutil.parser


class Speech:
    def __init__(self, config):
        self.filename = config['filename']
        self.filenamev = config['filenamev']

        self.synthesizeAudio = speechkit.SynthesizeAudio(
            config['api_key'], config['catalog'])
        self.recognizeShortAudio = speechkit.RecognizeShortAudio(
            config['api_key'])
        self.recognizer = sr.Recognizer()

        # self.scheduler = sched.scheduler(time.time, time.sleep)

    def speak(self, text):
        print(text)
        self.synthesizeAudio.synthesize(text, self.filename)

        AudioSegment.from_file(self.filename).export(
            self.filenamev, format="wav")
        speechkit.removefile(self.filename)

        playsound(self.filenamev)
        speechkit.removefile(self.filenamev)


def load_db(filename='data.json'):
    """load data from binary database as python object"""

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except json.decoder.JSONDecodeError:
        return 0
    except FileNotFoundError:
        return 0

    return data


def write_db(data, filename='data.json'):
    """write data as python object to the binary database"""

    try:
        with open(filename, 'w') as f:
            print(data)
            json.dump(data, f)
    # except pickle.PicklingError:
        # return 0
    except FileNotFoundError:
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
        config,
        speech: Speech,
        host="http://127.0.0.1:8000",
    ):
        self.config = config
        self.speech = speech
        self.token = config['token']
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
                self.tasks[key]
            except KeyError:
                break

        self.tasks[key] = task

    def __notifications_loop__(self):
        for i in self.data:
            now = datetime.now().astimezone()
            if not i['show']:
                continue

            if (now - dateutil.parser.isoparse(i['last_push'])).seconds//3600 > 1:
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

    def __execute_task__(self, task_id):
        task = self.tasks[task_id]

        self.speech.speak("Привет! Вам необходимо произвести измермерение и отправить врачу. Сможете это сделать сейчас?")

        status = None

        with sr.Microphone() as source:
            data = self.speech.recognizer.listen(source)
            data_sound = data.get_raw_data(convert_rate=48000)
            recognize_text = self.speech.recognizeShortAudio.recognize(
                data_sound, self.config['catalog'])
            print(recognize_text)

        if "да" in recognize_text.lower():
            self.speech.speak("Пожалуйста, произведите измерение {}. {}".format(
                task['alias'],
                "Укажите значение в "+task['unit'] if task['unit'] != "" else ""
            ))
            status = True
        else:
            self.speech.speak("Напоминание отложено на час")

        if status:
            input("Нажмите для того, чтобы проговорить значение")

            with sr.Microphone() as source:
                data = self.speech.recognizer.listen(source)
                data_sound = data.get_raw_data(convert_rate=48000)
                recognize_text = self.speech.recognizeShortAudio.recognize(
                    data_sound, self.config['catalog'])
                print(recognize_text)

            value = float(recognize_text.replace(" ", ""))

            answer = requests.post(self.host+'/speakerapi/pushvalue/', json={
                "token": self.token,
                "data": [(task['name'], value)],
            })
            if answer.status_code == 200:
                self.speech.speak("Значение успешно записано")
            else:
                self.speech.speak("Произошла ошибка при сохраниении измерения")
                print(answer, answer.text)

            self.data.pop(task_id)
        else:
            task['hours'] += 1
            task['days_week_hour'] += 1
            task['days_month_hour'] += 1
            self.data[task_id] = task

    def main_loop(self):
        self.__notifications_loop__()

        if len(self.tasks) > 0:
            print("TASKS:", self.tasks)
            for i in self.tasks:
                self.__execute_task__(i)

        time.sleep(60)

        if datetime.now().minute in [0, 30]:
            self.data = self.__get_data__()

            if write_db(self.data) == 0:
                print("ERROR WITH SAVING DATA")
