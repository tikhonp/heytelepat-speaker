import utils.speech as speech
import dateutil.parser
from datetime import datetime
from secrets import token_hex
import requests
from threading import Thread


class NotificationsAgentThread(Thread):
    """
    Agent for managering notifications
    It loads from server and save to local data
    with specified user notification settings.
    It creates tametabele agent and sends voice notifications.
    """
    def __init__(
        self,
        notifications: list,
        config,
        inputFunction,
        timeEvent,
        speech: speech.Speech,
        lock_obj,
        host="http://127.0.0.1:8000",
    ):
        Thread.__init__(self)
        self.config = config
        self.speech = speech
        self.inputFunction = inputFunction
        self.host = host
        self.timeEvent = timeEvent
        self.lock = lock_obj
        self.notifications = []

        for i in notifications:
            self.notifications.append(
                i(config, inputFunction, timeEvent, speech, host, lock_obj))

    def run(self):
        while True:
            for i in self.notifications:
                i.main_loop_item()
                self.timeEvent.wait(5)


class MessageNotification:
    def __init__(self, config, inputFunction, timeEvent, speech, host, lock):
        self.config = config
        self.speech = speech
        self.token = config['token']
        self.host = host
        self.inputFunction = inputFunction
        self.timeEvent = timeEvent
        self.lock = lock

    def __play__(self, text: str):
        synthesizedSpeech = self.speech.create_speech(text)
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()

    def main_loop_item(self):
        answer = requests.get(
            self.host+'/speakerapi/incomingmessage/',
            json={"token": self.token, "last_messages": False},
        )

        if answer.status_code == 200:
            print(
                "ERROR WITH GETTING DATA FROM SERVER!\nStatus code: {}\nAnswer: {}".format(
                    answer.status_code, answer.text))
            return

        answer = answer.json()
        if answer == []:
            return

        with self.lock:
            text = answer[0]["fields"]
            self.__play__(
                "Вам пришло новое сообщение, "+text)


class MeasurementNotification:
    def __init__(self, config, inputFunction, timeEvent, speech, host, lock):
        self.config = config
        self.speech = speech
        self.token = config['token']
        self.host = host
        self.data = self.__get_data__()
        self.inputFunction = inputFunction
        self.timeEvent = timeEvent
        self.lock = lock
        self.tasks = {}

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

            if (now - dateutil.parser.isoparse(
                    i['last_push'])).seconds//3600 > 1:
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

    def __repeat_recognition__(self, n=1):
        synthesizedSpeech = self.speech.create_speech(
            "Я не расслышал, повторите, пожалуйста еще.")
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()
        recognizeSpeech = self.speech.read_audio()

        if recognizeSpeech is None:
            n -= 1
            if n == 0:
                return None
            else:
                return self.__repeat_recognition__()
        else:
            text = recognizeSpeech.recognize()
            if text is None:
                n -= 1
                if n == 0:
                    return None
                else:
                    return self.__repeat_recognition__()
            else:
                return text

    def __play__(self, text: str):
        synthesizedSpeech = self.speech.create_speech(text)
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()

    def __execute_task__(self, task_id):
        task = self.tasks[task_id]

        self.__play__("Привет! Вам необходимо произвести измермерение и отправить врачу. Сможете это сделать сейчас?")

        status = None

        recognizeSpeech = self.speech.read_audio()
        if recognizeSpeech is None:
            text = self.__repeat_recognition__()
            if text is None:
                return
        else:
            text = recognizeSpeech.recognize()

        if "да" in text.lower():
            text_speak = "Пожалуйста, произведите измерение {}. {}".format(
                task['alias'],
                "Укажите значение в "+task['unit'] if task['unit'] != "" else ""
            )
            self.__play__(text_speak)

            status = True
        else:
            self.__play__("Напоминание отложено на час")

        if status:
            self.inputFunction()

            recognizeSpeech = self.speech.read_audio()
            if recognizeSpeech is None:
                text = self.__repeat_recognition__()
                if text is None:
                    return
            else:
                text = recognizeSpeech.recognize()

            value = float(text.replace(" ", ""))

            answer = requests.post(self.host+'/speakerapi/pushvalue/', json={
                "token": self.token,
                "data": [(task['name'], value)],
            })
            if answer.status_code == 200:
                self.__play__("Значение успешно записано")
            else:
                self.__play__("Произошла ошибка при сохраниении измерения")
                print(answer, answer.text)

            self.data.pop(task_id)
        else:
            task['hours'] += 1
            task['days_week_hour'] += 1
            task['days_month_hour'] += 1
            self.data[task_id] = task

    def main_loop_item(self):
        self.__notifications_loop__()

        if len(self.tasks) > 0:
            print("TASKS:", self.tasks)
            for i in self.tasks:
                with self.lock:
                    self.__execute_task__(i)

        if datetime.now().minute in [0, 30]:
            self.data = self.__get_data__()


notifications_list = [MeasurementNotification, MessageNotification]
