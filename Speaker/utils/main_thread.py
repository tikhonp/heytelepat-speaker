from threading import Thread
import requests
import locale
import datetime
import RPi.GPIO as GPIO


def simpleInputFunction():
    input("Press enter and tell something!")


def raspberryInputFunction():
    print("Waiting button...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN, GPIO.PUD_UP)

    while True:
        if GPIO.input(4) == GPIO.LOW:
            print("Button was pushed!")
            return


def exceptionHandler(ex):
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    print(message)


class MainThread(Thread):
    """
    Main thread represents user input
    """

    def __init__(self, objectStorage, activitiesList):
        """
        :param objectStorage: ObjectStorage instance
        :param activitiesList: dictionary of activities
        """
        Thread.__init__(self)
        self.objectStorage = objectStorage
        self.inputFunction = objectStorage.inputFunction
        self.activitiesList = activitiesList
        self.speech = objectStorage.speech
        self.token = objectStorage.config['token']
        self.domain = objectStorage.host
        self.lock = objectStorage.lock_obj
        self.speakSpeech = objectStorage.speakSpeech

    def __repeat_recognition__(self, n=1):
        self.speakSpeech.play(
            "Я не расслышал, повторите, пожалуйста еще.", cashed=True)

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

    def __get_action__(self, text: str):
        for i in self.activitiesList:
            if i in text.lower():
                return self.activitiesList[i]

        return None

    def __main_loop_item__(self):
        self.inputFunction()

        with self.lock:
            self.speech.adjust_for_ambient_noise(duration=0.5)
            recognizeSpeech = self.speech.read_audio()

            if recognizeSpeech is None:
                text = self.__repeat_recognition__()
                if text is None:
                    return
            else:
                text = recognizeSpeech.recognize()

            action = self.__get_action__(text)
            if action is None:
                self.speakSpeech.play(
                    "К сожалению, я еще не знаю такой команды.", cashed=True)
                return

            a = action(self.objectStorage)
            a.run()

    def run(self):
        while True:
            #try:
            self.__main_loop_item__()
            #except Exception as e:
            #    exceptionHandler(e)


class PresureTestAction:
    def __init__(self, objectStorage):
        self.speech = objectStorage.speech
        self.name = "Presure Test"
        self.inputFunction = objectStorage.inputFunction
        self.speakSpeech = objectStorage.speakSpeech

    def __execute_task__(self):
        self.speakSpeech.play(
            "Привет! Вам необходимо произвести измермерение и отправить врачу.", cashed=True)

        text_speak = "Пожалуйста, произведите измерение {}. {} Когда будете готовы нажмите на конпку и произнесите значение верхннего давления".format(
                "давления",
                "")
        self.speakSpeech.play(text_speak, cashed=True)

        self.inputFunction()

        recognizeSpeech = self.speech.read_audio()
        if recognizeSpeech is None:
            text = self.__repeat_recognition__()
            if text is None:
                return
        else:
            text = recognizeSpeech.recognize()

        try:
            svalue = int(text.replace(" ", ""))
        except:
            self.speakSpeech.play(
                "Значение не соответвсует", cashed=True)
            return

        self.speakSpeech.play(
            "Произведите измеренние ниижнего давления", cashed=True)

        recognizeSpeech = self.speech.read_audio()
        if recognizeSpeech is None:
            text = self.__repeat_recognition__()
            if text is None:
                return
        else:
            text = recognizeSpeech.recognize()

        try:
            dvalue = int(text.replace(" ", ""))
        except:
            self.speakSpeech.play(
                "Значение не соответвсует", cashed=True)
            return

        answer = requests.post('https://medsenger.ru/api/agents/records/add', json={
            "api_key": '$2y$10$EhnTCMUX3m1MdzJoPc5iQudhoLvZSyWPXV463/yH.EqC3qV9CSir2',
            "contract_id": 3188,
            "category_name": "systolic_pressure",
            "value": svalue,
        })
        if answer.status_code == 200:
            pass
        else:
            self.speakSpeech.play(
                "Произошла ошибка при сохраниении измерения", cashed=True)
            print(answer, answer.text)

        answer = requests.post('https://medsenger.ru/api/agents/records/add', json={
            "api_key": '$2y$10$EhnTCMUX3m1MdzJoPc5iQudhoLvZSyWPXV463/yH.EqC3qV9CSir2',
            "contract_id": 3188,
            "category_name": "diastolic_pressure",
            "value": dvalue,
        })
        if answer.status_code == 200:
            pass
        else:
            self.speakSpeech.play(
                "Произошла ошибка при сохраниении измерения", cashed=True)
            print(answer, answer.text)

        self.speakSpeech.play(
            "Значение успешно записано", cashed=True)

    def run(self):
        self.__execute_task__()


class TimeAction:
    def __init__(self, objectStorage):
        self.name = "Time"
        self.speakSpeech = objectStorage.speakSpeech
        locale.setlocale(locale.LC_TIME, "ru_RU")

    def run(self):
        timestr = datetime.datetime.now().astimezone().strftime(
            "%A, %-d %B, %H:%M")
        timestr = "Сейчас " + timestr + "."
        self.speakSpeech.play(timestr)


class NewMessagesAction:
    def __init__(self, objectStorage):
        self.name = "NewMessages"
        self.token = objectStorage.config['token']
        self.domen = objectStorage.host
        self.speakSpeech = objectStorage.speakSpeech

    def run(self):
        data = {
            'token': self.token,
            'last_messages': True
        }
        answer = requests.get(self.domen+'/speakerapi/incomingmessage/',
                              json=data)

        if answer.status_code != 200:
            self.speakSpeech.play(
                "Произошла ошибка при загрузке сообщений", cashed=True)
            print(answer, answer.text)
            return

        answer = answer.json()
        print(answer)

        if len(answer) == 0:
            self.speakSpeech.play(
                "Новых сообщений нет", cashed=True)
        else:
            for i in answer:
                text = "Сообщение. " + i['fields']['text']
                self.speakSpeech.play(text)
                self.timeEvent.wait(0.5)


class SendMessageAction:
    def __init__(self, objectStorage):
        self.name = "SendMessage"
        self.token = objectStorage.config['token']
        self.domen = objectStorage.host
        self.speech = objectStorage.speech
        self.speakSpeech = objectStorage.speakSpeech
        self.timeEvent = objectStorage.event_obj

    def __repeat_recognition__(self, n=1):
        self.speakSpeech.play(
            "Я не расслышал, повторите, пожалуйста еще.", cashed=True)

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

    def run(self):
        self.speakSpeech.play(
            "Какое сообщение вы хотите отправить?", cashed=True)

        recognizeSpeech = self.speech.read_audio()

        if recognizeSpeech is None:
            text = self.__repeat_recognition__()
            if text is None:
                return
        else:
            text = recognizeSpeech.recognize()

        answer = requests.post(self.domen+"/speakerapi/sendmessage/", json={
            'token': self.token,
            'message': text,
        })

        if answer.status_code == 200:
            text = "Сообщение успешно отправлено!"
        else:
            text = "Произошла ошибка приотправлении сообщения"
            print(answer, answer.text)

        self.speakSpeech.play(text, cashed=True)


activitiesList = {
    "время": TimeAction,
    "отправь сообщени": SendMessageAction,
    "давление": PresureTestAction,
    "новое сообщение": NewMessagesAction,
}
