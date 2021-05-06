from threading import Thread
import requests
import locale
import datetime
import utils.speech as speech
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
        self.speech = objectStorage.speech_cls
        self.token = objectStorage.config['token']
        self.domain = objectStorage.domain
        self.lock = objectStorage.lock_obj

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
                synthesizedSpeech = self.speech.create_speech(
                    "К сожалению, я еще не знаю такой команды.")
                synthesizedSpeech.syntethize()
                synthesizedSpeech.play()
                return

            a = action(self.objectStorage)
            a.run()

    def run(self):
        while True:
            try:
                self.__main_loop_item__()
            except Exception as e:
                exceptionHandler(e)


class PresureTestAction:
    def __init__(self, objectStorage):
        self.speech = objectStorage.speech_cls
        self.name = "Presure Test"
        self.inputFunction = objectStorage.inputFunction

    def __play__(self, text: str):
        synthesizedSpeech = self.speech.create_speech(text)
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()

    def __execute_task__(self):
        self.__play__("Привет! Вам необходимо произвести измермерение и отправить врачу.")

        text_speak = "Пожалуйста, произведите измерение {}. {} Когда будете готовы нажмите на конпку и произнесите значение верхннего давления".format(
                "давления",
                ""
            )
        self.__play__(text_speak)


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
            self.__play__("Знвчение не соответвсует")
            return

        self.__play__("Произведите измеренние ниижнего давления")

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
            self.__play__("Знвчение не соответвсует")
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
            self.__play__("Произошла ошибка при сохраниении измерения")
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
            self.__play__("Произошла ошибка при сохраниении измерения")
            print(answer, answer.text)

        self.__play__("Значение успешно записано")

    def run(self):
        self.__execute_task__()


class TimeAction:
    def __init__(self, objectStorage):
        self.name = "Time"
        self.speech = objectStorage.speech_cls
        locale.setlocale(locale.LC_TIME, "ru_RU")

    def run(self):
        timestr = datetime.datetime.now().astimezone().strftime(
            "%A, %-d %B, %-H:%-M")
        timestr = "Сейчас " + timestr + "."
        synthesizedSpeech = self.speech.create_speech(timestr)
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()


class SendMessageAction:
    def __init__(self, objectStorage):
        self.name = "SendMessage"
        self.token = objectStorage.config['token']
        self.domen = objectStorage.domen
        self.speech = objectStorage.speech_cls

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

    def run(self):
        synthesizedSpeech = self.speech.create_speech(
            "Какое сообщение вы хотите отправить?")
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()
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
            speech.speak("Произошла ошибка приотправлении сообщения")
            print(answer, answer.text)

        synthesizedSpeech = self.speech.create_speech(text)
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()
        recognizeSpeech = self.speech.read_audio()


activitiesList = {
    "время": TimeAction,
    "сообщени": SendMessageAction,
    "давление": PresureTestAction,
}
