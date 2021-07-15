import asyncio
import logging
import json

from dialogs.measurments_dialogs import (
    AddValueDialog,
)
from events.event import EventDialog


class MeasurementNotificationDialog(AddValueDialog):
    data = None
    ws = None

    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            self.data['patient_description']
            + " Вы готовы произнести ответ сейчас?", cashed=True)
        asyncio.new_event_loop().run_until_complete(
            self.ws.send(json.dumps({
                'token': self.objectStorage.token,
                'request_type': 'is_sent',
                'measurement_id': self.data['id'],
            })))
        self.cur = self.yes_no

    def yes_no(self, _input):
        if 'да' in _input.lower():
            self.category = self.data['fields'].pop(0)
            self.objectStorage.speakSpeech.play(
                "Произнесите значение {}".format(self.category.get('text')))
            self.cur = self.third
            self.need_permanent_answer = True
            return
        else:
            self.objectStorage.speakSpeech.play(
                "Введите значение позже с помощию"
                " команды 'запистать значение'", cashed=True)
            return

    cur = first


class MeasurementNotificationEvent(EventDialog):
    dialog_class = MeasurementNotificationDialog

    def on_message(self, message):
        self.data = json.loads(message)
        self.event_happend = True
        logging.debug("New message from socket: {}".format(self.data))

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        loop = asyncio.new_event_loop()
        while True:
            loop.run_until_complete(
                self.webSocketConnect(
                    'ws/speakerapi/measurements/',
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
        return dialog

    name = "Уведомление об измерении"
