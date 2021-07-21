from dialogs.dialog import Dialog
import datetime
import locale
import logging
try:
    import alsaaudio
except ImportError:
    logging.warning(
        "AlsaAudio import error, make sure development mode is active")
    alsaaudio = None


locale.setlocale(locale.LC_TIME, "ru_RU")


class TimeDialog(Dialog):
    def first(self, text):
        str_formatted_time = datetime.datetime.now().astimezone().strftime(
            "%A, %-d %B, %H:%M")
        str_formatted_time = "Сейчас " + str_formatted_time + "."
        self.objectStorage.speakSpeech.play(str_formatted_time)

    cur = first
    name = 'Время'
    keywords = ['время', 'час']


class SetVolumeDialog(Dialog):
    def first(self, text):
        if alsaaudio is None:
            return
        self.objectStorage.speakSpeech.play(
                "Какую громкость вы хотите поставить?", cache=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, text):
        if not (value := self.to_integer(text)):
            self.objectStorage.speakSpeech.play(
                    "Необходимо указать числовое значение", cache=True)
            return

        if value < 1 or value > 100:
            self.objectStorage.speakSpeech.play(
                "Необходимо значение в промежутке от 1 до 100", cache=True)
            return

        m = alsaaudio.Mixer(control='Speaker', cardindex=1)
        m.setvolume(value)

        self.objectStorage.speakSpeech.play(
                "Громкость установлена", cache=True)

    cur = first
    name = 'Громкость'
    keywords = ['громкость']


class HelpDialog(Dialog):
    def first(self, text):
        self.objectStorage.speakSpeech.play(
            "Я знаю очень много вещей, например 'который час' и умею общаться с вашим врачом. "
            "Попросите меня отправить сообщение врачу или спросите: "
            "'Расскажи о непрочитанных сообщениях', и я прочитаю новые сообщения от врача. "
            "Я напомню о необходимых опросниках, которые нужно направить врачу, "
            "а если вы пропустите просто попросите: 'Заполнить опросники.' "
            "Если вам нужно передать только одно измерение произнесите: 'Записать значение измерения.' "
            "Чтобы не забыть о лекарствах, спросите 'Какие лекарства мне нужно принять?', "
            "А чтобы подтвердить прием лекарства скажите 'Подтверди прием.'", cache=True
        )
    cur = first
    name = 'Помощь'
    keywords = ['умеешь']
