from events.event import Event
from dialogs.dialog import Dialog
import logging
import json
import asyncio


class MessageNotificationDialog(Dialog):
    data = None
    ws = None

    def first(self, _input):
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
            "Пометить сообщение как прочитанное?", cashed=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, _input):
        if 'да' in _input.lower():
            asyncio.new_event_loop().run_until_complete(
                self.ws.send(json.dumps({
                    "token": self.objectStorage.token,
                    "red_message": True,
                    "message_id": self.data.get('id')
                })))
            self.objectStorage.speakSpeech.play(
                "Отлично!", cashed=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Сообщение не помечено как прочитанное", cashed=True)

    cur = first
    name = 'Уведомление о новом сообщении'


class MessageNotificationEvent(Event):
    dialog_class = MessageNotificationDialog

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
                    'ws/speakerapi/incomingmessage/',
                    {"token": self.objectStorage.token},
                    self.on_message,
                ))

    def return_dialog(self, *args, **kwargs):
        dialog = self.get_dialog(self.objectStorage)
        dialog.data = self.data
        dialog.ws = self.ws
        return dialog

    name = 'Уведомление о новом сообщении'
