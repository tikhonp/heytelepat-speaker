from dialogs.dialog import Dialog
import datetime
import locale


locale.setlocale(locale.LC_TIME, "ru_RU")


class TimeDialog(Dialog):
    def first(self, _input):
        timestr = datetime.datetime.now().astimezone().strftime(
            "%A, %-d %B, %H:%M")
        timestr = "Сейчас " + timestr + "."
        self.objectStorage.speakSpeech.play(timestr)

    cur = first
    name = 'Время'
    keywords = ('время', 'час')
