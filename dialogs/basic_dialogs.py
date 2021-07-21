from dialogs.dialog import Dialog
import datetime
import locale
import logging
try:
    import alsaaudio
except ImportError:
    logging.warning(
        "AlsaAudio import error, make shure development mode is active")


locale.setlocale(locale.LC_TIME, "ru_RU")


class TimeDialog(Dialog):
    def first(self, _input):
        timestr = datetime.datetime.now().astimezone().strftime(
            "%A, %-d %B, %H:%M")
        timestr = "Сейчас " + timestr + "."
        self.objectStorage.speakSpeech.play(timestr)

    cur = first
    name = 'Время'
    keywords = ['время', 'час']


class SetVolumeDialog(Dialog):
    def first(self, _input):
        self.objectStorage.speakSpeech.play(
                "Какую громкость вы хотите поставить?", cache=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, _input):
        if not _input.isdigit():
            self.objectStorage.speakSpeech.play(
                    "Необходимо указать числовое значение", cache=True)
            return

        v = int(_input)
        if v < 1 or v > 100:
            self.objectStorage.speakSpeech.play(
                "Необходимо значение в промежутке от 1 до 100", cache=True)
            return

        m = alsaaudio.Mixer(control='Speaker', cardindex=1)
        m.setvolume(v)

        self.objectStorage.speakSpeech.play(
                "Громкость установлена", cache=True)

    cur = first
    name = 'Громкость'
    keywords = ['громкость']


class HelpDialog(Dialog):
    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Я знаю очень много вещей, например 'который час' и умею общаться с вашим врачём. "
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
