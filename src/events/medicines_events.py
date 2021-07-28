import asyncio
import json
from abc import ABC

from dialogs.dialog import Dialog
from events.event import Event


class MedicineNotificationDialog(Dialog):
    data = None
    ws = None
    loop = None

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            "Вам необходимо принять препарат {}. {}. ".format(self.data['title'], self.data['rules']) +
            "Подтвердите, вы приняли препарат?"
        )
        self.loop.create_task(
            self.ws.send(json.dumps({
                'token': self.objectStorage.token,
                'request_type': 'is_sent',
                'measurement_id': self.data['id'],
            })))
        self.cur = self.yes_no

    def yes_no(self, text):
        if self.is_positive(text):
            self.loop.create_task(
                self.ws.send(json.dumps({
                    'token': self.objectStorage.token,
                    'request_type': 'pushvalue',
                    'value': self.data['title'],
                })))
            self.loop.create_task(
                self.ws.send(json.dumps({
                    'token': self.objectStorage.token,
                    'request_type': 'is_done',
                    'measurement_id': self.data['id'],
                })))
            self.objectStorage.speakSpeech.play("Отлично!", cache=True)
        elif self.is_negative(text):
            self.objectStorage.speakSpeech.play(
                "Подтвердите прием позже с помощью комманды 'какие лекарства необходимо принять'", cache=True
            )
        else:
            self.objectStorage.speakSpeech.play(
                "Извините, я вас не очень поняла", cashe=True
            )

    cur = first
    name = 'Уведомление о принятии лекарства'


class MedicineNotificationEvent(Event, ABC):
    name = "Уведомление о лекарствах"

    async def loop_item(self):
        await self.web_socket_connect(
            '/ws/speakerapi/medicines/',
            {
                "token": self.object_storage.token,
                "request_type": "init"
            },
        )

    async def return_dialog(self, *args, **kwargs):
        self.dialog_class = MedicineNotificationDialog
        dialog = await self.get_dialog(self.object_storage)
        dialog.data = self.data
        dialog.ws = self.ws
        dialog.loop = self.loop
        return dialog
