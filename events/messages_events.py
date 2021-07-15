from events.event import EventDialog
from dialogs.dialog import Dialog
import logging
import json
import asyncio


class MessageNotificationDialog(Dialog):
    text = None
    m_id = None
    ws = None

    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Вам пришло новое сообщение, "+self.text)
        asyncio.new_event_loop().run_until_complete(
            self.ws.send(json.dumps({
                "token": self.objectStorage.token,
                "notified_message": True,
                "message_id": self.m_id
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
                    "message_id": self.m_id
                })))
            self.objectStorage.speakSpeech.play(
                "Отлично!", cashed=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Сообщение не помечено как прочитанное", cashed=True)

    cur = first
    name = 'Уведомление о новом сообщении'


class MessageNotificationEvent(EventDialog):
    dialog_class = MessageNotificationDialog

    def on_message(self, message):
        try:
            data = json.loads(message)
        except json.decoder.JSONDecodeError:
            logging.error("Error decoding message '%s'", message)
            return
        try:
            self.text = data['text']
            self.m_id = data['id']
        except KeyError:
            logging.error("Invalid keys in data '%s'", data)
            return
        self.event_happend = True

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        loop = asyncio.new_event_loop()
        while True:
            loop.run_until_complete(
                self.webSocketConnect(
                    'ws/speakerapi/incomingmessage/',
                    {
                        "token": self.objectStorage.token,
                    },
                    self.on_message,
                ))

    def return_dialog(self, *args, **kwargs):
        dialog = self.get_dialog(self.objectStorage)
        dialog.text = self.text
        dialog.m_id = self.m_id
        dialog.ws = self.ws
        return dialog

    name = 'Уведомление о новом сообщении'
