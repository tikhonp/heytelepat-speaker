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
import pygame
from os import system


def load_db(filename='data.pickle'):
    """load data from binary database as python object"""

    try:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
    except pickle.UnpicklingError:
        return 0
    except FileNotFoundError:
        return 0

    return data


def write_db(data, filename='data.pickle'):
    """write data as python object to the binary database"""

    try:
        with open(filename, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError:
        return 0
    except FileNotFoundError:
        return 0


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
        
        cmd = "ffmpeg -i '{}' -ar 44100 -ac 1 out.wav".format(self.filenamev)
        out = system(cmd)

        pygame.mixer.pre_init(48000, 32, 2, 4096)
        pygame.mixer.init()
        pygame.mixer.music.load("out.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

        speechkit.removefile(self.filenamev)
        speechkit.removefile("out.wav")


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
        speech: Speech,
        host="http://tikhonsystems.ddns.net",
    ):
        self.config = config
        self.speach = speech
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

    def __execute_task__(self, task_id):
        task = self.data[task_id]

        speech.speak("Привет! Вам необходимо произвести измермерение и отправить врачу. Сможете это сделать сейчас?")

        status = None

        with sr.Microphone() as source:
            data = speech.recognizer.listen(source)
            data_sound = data.get_raw_data(convert_rate=48000)
            recognize_text = speech.recognizeShortAudio.recognize(
                data_sound, config['catalog'])
            print(recognize_text)

        if "да" in recognize_text.lower():
            speech.speak("Пожалуйста, произведите измерение {}. {}".format(
                task['alias'],
                "Укажите значение в "+task['unit'] if task['unit'] != "" else ""
            ))
            status = True
        else:
            speech.speak("Напоминание отложено на час")

        if status:
            input("Нажмите для того, чтобы проговорить значение")

            with sr.Microphone() as source:
                data = speech.recognizer.listen(source)
                data_sound = data.get_raw_data(convert_rate=48000)
                recognize_text = speech.recognizeShortAudio.recognize(
                    data_sound, config['catalog'])
                print(recognize_text)

            value = float(recognize_text.replace(" ", ""))

            answer = requests.post(self.host+'speakerapi/pushvalue/', json={
                "token": self.token,
                "data": [(task['name'], value)],
            })
            if answer.status_code == 200:
                speech.speak("Значение успешно записано")
            else:
                speech.speak("Произошла ошибка при сохраниении измерения")
                print(answer, answer.text)

            self.data.pop(task_id)
        else:
            task['hours'] += 1
            task['days_week_hour'] += 1
            task['days_month_hour'] += 1
            self.data[task_id] = task

    def main_loop(self):
        self.__notifications_loop__()

        if len(self.data) > 0:
            for i in self.data:
                self.__execute_task__(i)

        time.sleep(60)

        if datetime.now().minute in (0, 30):
            self.data = self.__get_data__()

            if write_db(self.data) == 0:
                print("ERROR WITH SAVING DATA")


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

        with open("speaker_config.json", "w") as f:
            f.write(json.dumps(config))
            print(config)

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

    notificationsagent = NotificationsAgent(
        config['token'],
        speech
    )

    notifications_t = threading.Thread(target=notificationsagent.main_loop)
    notifications_t.start()

    while True:
        input("Press enter and tell something!")

        with sr.Microphone() as source:
            data = speech.recognizer.listen(source)
            data_sound = data.get_raw_data(convert_rate=48000)
            recognize_text = speech.recognizeShortAudio.recognize(data_sound, config['catalog'])
        print(recognize_text)

        if recognize_text.lower() == "хватит":
            notifications_t.terminate()
            break

        for i in motions:
            if i in recognize_text.lower():
                motions[i](speech, config)
