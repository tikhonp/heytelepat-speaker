import dateutil.parser
from datetime import datetime
from secrets import token_hex
import requests
from threading import Thread
# from utils.main_thread import exceptionHandler


class NotificationsAgentThread(Thread):
    """
    Agent for managering notifications
    It loads from server and save to local data
    with specified user notification settings.
    It creates tametabele agent and sends voice notifications.
    """
    def __init__(
        self,
        objectStorage,
        notifications: list,
    ):
        Thread.__init__(self)
        self.config = objectStorage.config
        self.speech = objectStorage.speech
        self.inputFunction = objectStorage.inputFunction
        self.host = objectStorage.host
        self.timeEvent = objectStorage.event_obj
        self.lock = objectStorage.lock_obj
        self.notifications = [i(objectStorage) for i in notifications]
        self.speakSpeech = objectStorage.speakSpeech

    def run(self):
        while True:
            for i in self.notifications:
                # try:
                i.main_loop_item()
                # except Exception as e:
                #   exceptionHandler(e)

                self.timeEvent.wait(5)


class MessageNotification:
    def __init__(self, objectStorage):
        self.token = objectStorage.config['token']
        self.host = objectStorage.host
        self.speakSpeech = objectStorage.speakSpeech
        self.lock = objectStorage.lock_obj

    def main_loop_item(self):
        try:
            answer = requests.get(
                self.host+'/speakerapi/incomingmessage/',
                json={"token": self.token, "last_messages": False},
            )

            if answer.status_code != 200:
                print(
                    "ERROR WITH GETTING DATA FROM SERVER!\nStatus code: {}\nAnswer: {}".format(
                        answer.status_code, answer.text))
                return
        except requests.exceptions.ConnectTimeout:
            print("ERROR WITH GETTING DATA FROM SERVER! Timeout.") 
            self.speakSpeech.play(
                    "Сервер не доступен.", cache=True)
            return

        answer = answer.json()
        if answer == []:
            return

        with self.lock:
            text = answer[0]["fields"]["text"]
            self.speakSpeech.play(
                "Вам пришло новое сообщение, "+text)


class MeasurementNotification:
    def __init__(self, objectStorage):
        self.config = objectStorage.config
        self.speech = objectStorage.speech
        self.token = objectStorage.config['token']
        self.host = objectStorage.host
        self.data = self.__get_data__()
        self.inputFunction = objectStorage.inputFunction
        self.timeEvent = objectStorage.event_obj
        self.lock = objectStorage.lock_obj
        self.tasks = {}
        self.speakSpeech = objectStorage.speakSpeech

    def __get_data__(self):
        try:
            answer = requests.get(
                self.host+'/speakerapi/tasks/',
                json={"token": self.token},
                timeout=5,
            )
            if answer.status_code != 200:
                print(
                    "ERROR WITH GETTING DATA FROM SERVER!\nStatus code: {}\nAnswer: {}".format(
                        answer.status_code, answer.text))
                return []
        except requests.exceptions.ConnectTimeout:
            print("ERROR WITH GETTING DATA FROM SERVER! Timeout.")
            return []

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
        self.speakSpeech.play(
            "Я не расслышал, повторите, пожалуйста еще.", cache=True)

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

    def __execute_task__(self, task_id):
        task = self.tasks[task_id]

        self.speakSpeech.play(
            "Привет! Вам необходимо произвести измермерение и отправить врачу. Сможете это сделать сейчас?", cache=True)

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
            self.speakSpeech.play(text_speak)

            status = True
        else:
            self.speakSpeech.play("Напоминание отложено на час", cache=True)

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
                self.speakSpeech.play("Значение успешно записано", cache=True)
            else:
                self.speakSpeech.play(
                    "Произошла ошибка при сохраниении измерения",
                    cache=True
                )
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
