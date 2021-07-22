import asyncio
import json
import logging
from abc import ABC

from dialogs.measurments_dialogs import (
    AddValueDialog,
)
from events.event import Event


class MeasurementNotificationDialog(AddValueDialog):
    data = None
    ws = None
    dialog_time = None
    category = None

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            self.data['patient_description']
            + " Вы готовы произнести ответ сейчас?")
        asyncio.new_event_loop().run_until_complete(
            self.ws.send(json.dumps({
                'token': self.objectStorage.token,
                'request_type': 'is_sent',
                'measurement_id': self.data['id'],
            })))
        self.cur = self.yes_no

    def yes_no(self, text):
        if self.is_positive(text):
            self.category = self.data['fields'].pop(0)
            self.objectStorage.speakSpeech.play(
                "Произнесите значение {}".format(self.category.get('text')))
            self.cur = self.third
            self.need_permanent_answer = True
            return
        elif self.is_negative(text):
            self.objectStorage.speakSpeech.play(
                "Введите значение позже с помощию"
                " команды 'заполнить опросники'", cache=True)
            # dialog = self.__class__(self.object_storage)
            # dialog.data = self.data
            # dialog.ws = self.ws
            # dialog.dialog_time = self.dialog_time

            # self.dialog_time.append(
            # (datetime.datetime.now() + datetime.timedelta(minutes=5),
            # dialog))
        else:
            self.objectStorage.speakSpeech.play(
                "Извините, я вас не очень поняла", cashe=True
            )

    cur = first


class MeasurementNotificationEvent(Event, ABC):
    name = "Уведомление об измерении"
    dialog_class = MeasurementNotificationDialog
    dialog_time = []
    data = None

    def on_message(self, message):
        self.data = json.loads(message)
        self.event_happened = True
        logging.debug("New message from socket: {}".format(self.data))

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        loop = asyncio.new_event_loop()
        while True:
            loop.run_until_complete(
                self.web_socket_connect(
                    '/ws/speakerapi/measurements/',
                    {
                        "token": self.objectStorage.token,
                        "request_type": "init"
                    },
                    self.on_message,
                ))

    def return_dialog(self, *args, **kwargs):
        dialog = self.get_dialog(self.objectStorage)
        dialog.data = self.data
        dialog.ws = self.ws
        dialog.dialog_time = self.dialog_time
        return dialog

    def get_dialog_time(self):
        return self.dialog_time.pop(0) if self.dialog_time else False
