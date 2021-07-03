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
                "Какую громкость вы хотите поставить?", cashed=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, _input):
        if not _input.isdigit():
            self.objectStorage.speakSpeech.play(
                    "Необходимо указать числовое значение", cashed=True)
            return

        v = int(_input)
        if v < 1 or v > 100:
            self.objectStorage.speakSpeech.play(
                "Необходимо значение в промежутке от 1 до 100", cashed=True)
            return

        m = alsaaudio.Mixer(control='Speaker', cardindex=1)
        m.setvolume(v)

        self.objectStorage.speakSpeech.play(
                "Громкость установлена", cashed=True)

    cur = first
    name = 'Громкость'
    keywords = ['громкость']
