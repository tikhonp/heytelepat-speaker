import asyncio
import json
import logging

from dialogs.dialog import Dialog
from events.event import Event


class MedicineNotificationDialog(Dialog):
    data = None
    ws = None

    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Вам необходимо принять препарат {}. {}. ".format(self.data['title'], self.data['rules']) +
            "Подтвердите, вы приняли препарат?"
        )
        asyncio.new_event_loop().run_until_complete(
            self.ws.send(json.dumps({
                'token': self.objectStorage.token,
                'request_type': 'is_sent',
                'measurement_id': self.data['id'],
            })))
        self.cur = self.yes_no

    def yes_no(self, _input):
        if 'да' in _input.lower():
            asyncio.new_event_loop().run_until_complete(
                self.ws.send(json.dumps({
                    'token': self.objectStorage.token,
                    'request_type': 'pushvalue',
                    'value': self.data['title'],
                })))
            asyncio.new_event_loop().run_until_complete(
                self.ws.send(json.dumps({
                    'token': self.objectStorage.token,
                    'request_type': 'is_done',
                    'measurement_id': self.data['id'],
                })))
            self.objectStorage.speakSpeech.play("Отлично!", cashed=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Подтвердите прием позже с помощью комманды 'какие лекарства необходимо принять'", cashed=True
            )

    cur = first
    name = 'Уведомление о принятии лекарства'


class MedicineNotificationEvent(Event):
    name = "Уведомление о лекарствах"
    dialog_class = MedicineNotificationDialog
    data = None

    def on_message(self, msg: str):
        self.data = json.loads(msg)
        self.event_happened = True
        logging.debug("New message from socket: {}".format(self.data))

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        loop = asyncio.new_event_loop()
        while True:
            loop.run_until_complete(
                self.web_socket_connect(
                    'ws/speakerapi/medicines/',
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
