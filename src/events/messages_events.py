import asyncio
import json
import logging
from abc import ABC

from dialogs.dialog import Dialog
from events.event import Event


class MessageNotificationDialog(Dialog):
    data = None
    ws = None
    loop = None

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            "{} вам, только что написал: {}.".format(
                self.data.get('sender'), self.data.get('text'))
        )
        self.loop.create_task(
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
            self.loop.create_task(
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
    name = 'Уведомление о новом сообщении'

    async def loop_item(self):
        await self.web_socket_connect(
            '/ws/speakerapi/incomingmessage/',
            {"token": self.object_storage.token},
        )

    async def return_dialog(self):
        self.dialog_class = MessageNotificationDialog
        dialog = await self.get_dialog(self.object_storage)
        dialog.data = self.data
        dialog.ws = self.ws
        dialog.loop = self.loop
        return dialog
