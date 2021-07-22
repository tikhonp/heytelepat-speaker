import asyncio
import json
import logging
from abc import ABC

from dialogs.dialog import Dialog
from events.event import Event


class MessageNotificationDialog(Dialog):
    data = None
    ws = None

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            "{} вам, только что написал: {}.".format(
                self.data.get('sender'), self.data.get('text'))
        )
        asyncio.new_event_loop().run_until_complete(
            self.ws.send(json.dumps({
                "token": self.objectStorage.token,
                "notified_message": True,
                "message_id": self.data.get('id')
            })))
        self.objectStorage.speakSpeech.play(
            "Пометить сообщение как прочитанное?", cache=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, text):
        if self.is_positive(text):
            asyncio.new_event_loop().run_until_complete(
                self.ws.send(json.dumps({
                    "token": self.objectStorage.token,
                    "red_message": True,
                    "message_id": self.data.get('id')
                })))
            self.objectStorage.speakSpeech.play(
                "Отлично!", cache=True)
        elif self.is_negative(text):
            self.objectStorage.speakSpeech.play(
                "Сообщение не помечено как прочитанное", cache=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Извините, я вас не очень поняла", cashe=True
            )

    cur = first
    name = 'Уведомление о новом сообщении'


class MessageNotificationEvent(Event, ABC):
    dialog_class = MessageNotificationDialog
    data = None

    def on_message(self, message):
        try:
            self.data = json.loads(message)
        except json.decoder.JSONDecodeError:
            logging.error("Error decoding message '%s'", message)
            return
        self.event_happened = True

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        loop = asyncio.new_event_loop()
        while True:
            loop.run_until_complete(
                self.web_socket_connect(
                    '/ws/speakerapi/incomingmessage/',
                    {"token": self.objectStorage.token},
                    self.on_message,
                ))

    def return_dialog(self, *args, **kwargs):
        dialog = self.get_dialog(self.objectStorage)
        dialog.data = self.data
        dialog.ws = self.ws
        return dialog

    name = 'Уведомление о новом сообщении'
