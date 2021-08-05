from abc import ABC

from events.event import Event, EventDialog


class MessageNotificationDialog(EventDialog):
    def first(self, _):
        self.objectStorage.speakSpeech.play(
            "{} вам, только что написал: {}.".format(
                self.data.get('sender'), self.data.get('text'))
        )
        self.send_ws_data({
            "token": self.objectStorage.token,
            "notified_message": True,
            "message_id": self.data.get('id')
        })
        self.objectStorage.speakSpeech.play(
            "Пометить сообщение как прочитанное?", cache=True)
        self.current_input_function = self.second
        self.need_permanent_answer = True
        self.call_later_delay = 15
        self.call_later_on_end = True

    def second(self, text):
        if self.is_positive(text):
            self.call_later_on_end = False
            self.send_ws_data({
                "token": self.objectStorage.token,
                "red_message": True,
                "message_id": self.data.get('id')
            })
            self.objectStorage.speakSpeech.play(
                "Отлично!", cache=True)
        elif self.is_negative(text):
            self.objectStorage.speakSpeech.play(
                "Сообщение не помечено как прочитанное", cache=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Извините, я вас не очень поняла", cashe=True
            )

    current_input_function = first
    name = 'Уведомление о новом сообщении'


class MessageNotificationEvent(Event, ABC):
    name = 'Уведомление о новом сообщении'

    async def loop_item(self):
        await self.web_socket_connect(
            'incomingmessage/',
            {"token": self.object_storage.token},
        )

    async def return_dialog(self, dialog_engine_instance):
        self.dialog_class = MessageNotificationDialog
        return await self.get_dialog(self.object_storage, self.data, self.ws, self.loop, dialog_engine_instance)
