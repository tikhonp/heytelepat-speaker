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
    category = None
    loop = None

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            self.data['patient_description']
            + " Вы готовы произнести ответ сейчас?")
        self.loop.create_task(
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
        else:
            self.objectStorage.speakSpeech.play(
                "Извините, я вас не очень поняла", cashe=True
            )

    cur = first


class MeasurementNotificationEvent(Event, ABC):
    name = "Уведомление об измерении"

    async def loop_item(self):
        await self.web_socket_connect(
            '/ws/speakerapi/measurements/',
            {
                "token": self.object_storage.token,
                "request_type": "init"
            },
        )

    async def return_dialog(self, *args, **kwargs):
        self.dialog_class = MeasurementNotificationDialog
        dialog = await self.get_dialog(self.object_storage)
        dialog.data = self.data
        dialog.ws = self.ws
        dialog.loop = self.loop
        return dialog
