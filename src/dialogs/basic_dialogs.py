import datetime
import locale
import logging
import time
import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning("RPi.GPIO is not available, button is disabled")

from dialogs.dialog import Dialog
from init_gates.config_gate import save_config

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


class ResetDialog(Dialog):
    last_time_pressed = None
    count_presses = 0
    button_pin = 17
    time_delay = 0.8

    def callback(self, event=None):
        current_time = int(time.time())
        if self.last_time_pressed is None:
            self.count_presses = 1
            self.last_time_pressed = current_time
        elif (current_time - self.last_time_pressed) < self.time_delay:
            self.count_presses += 1
            self.last_time_pressed = current_time
        else:
            self.last_time_pressed = None
            self.count_presses = 0

    def reset_speaker(self):
        self.objectStorage.speakSpeech.play("Восстанавливаю заводские настройки.", cashed=True)
        if not self.fetch_data(
                'delete',
                self.objectStorage.host_http + 'speaker/',
                json={'token': self.objectStorage.token}
        ):
            return
        config = self.objectStorage.config
        config['token'] = None
        save_config(config, self.objectStorage.config_filename)
        self.objectStorage.speakSpeech.play("Успешно восстановлены заводские настройки.", cashed=True)
        sys.exit()

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            "Для поддтверждения сброса колонки нажмите трижды на кнопку или один раз для отмены.", cashed=True
        )
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING, callback=self.callback, bouncetime=250)
        while True:
            if self.count_presses >= 3:
                return self.reset_speaker()
            if self.last_time_pressed and self.count_presses == 1 and \
                    (int(time.time()) - self.last_time_pressed) > self.time_delay:
                self.objectStorage.speakSpeech.play(
                    "Отменено.", cashed=True
                )
                return

    cur = first
    name = 'Сброс до заводских настроек'
    keywords = ['сброс', 'заводск']