from threading import Thread
import requests
import locale
import datetime
import utils.speech as speech
import RPi.GPIO as GPIO


def inputFunction():
    input("Press enter and tell something!")


def raspberryInputFunction():
    print("Waiting button")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    while True:
        if GPIO.input(4) == GPIO.HIGH:
            print("Button was pushed!")
            return


class MainThread(Thread):
    """
    Main thread represents user input
    """

    def __init__(self,
                 inputFunction,
                 activitiesList,
                 token: str,
                 domain: str,
                 speech_cls: speech.Speech,
                 lock_obj,
                 ):
        """
        :param inputFunction: Input function that ask button like objects
        :param activitiesList: dictionary of activities
        :param token: string token of serverside
        :param domain: string domain of server
        :param speech: object of Speech class
        """

        Thread.__init__(self)
        self.inputFunction = inputFunction
        self.activitiesList = activitiesList
        self.speech = speech_cls
        self.token = token
        self.domain = domain
        self.lock = lock_obj

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

            a = action(self.speech, self.token, self.domain)
            a.run()

    def run(self):
        while True:
            # try:
            self.__main_loop_item__()
            # except Exception as e:
                # print(e)


class Action:
    """
    class that represents action function
    """

    def __init__(self, speech_cls):
        """
        :param speech: object of Speech class
        """
        self.name = "unknown"
        self.runningState = False
        self.speech = speech_cls

    def run(self):
        self.runningState = True
        pass

    def stop(self):
        self.runningState = False


class TimeAction(Action):
    def __init__(self, speech_cls, *args):
        Action.__init__(self, speech_cls)
        self.name = "Time"
        locale.setlocale(locale.LC_TIME, "ru_RU")

    def run(self):
        timestr = datetime.datetime.now().astimezone().strftime(
            "%A, %-d %B, %-H:%-M")
        timestr = "Сейчас " + timestr + "."
        synthesizedSpeech = self.speech.create_speech(timestr)
        synthesizedSpeech.syntethize()
        synthesizedSpeech.play()


class SendMessageAction(Action):
    def __init__(self, speech_cls, token, domen):
        Action.__init__(self, speech_cls)
        self.name = "SendMessage"
        self.token = token
        self.domen = domen

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
}
