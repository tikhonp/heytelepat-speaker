from abc import ABC

from events.event import Event, EventDialog


class MedicineNotificationDialog(EventDialog):
    def first(self, _):
        self.objectStorage.play_speech.play(
            "Вам необходимо принять препарат {}. {}. ".format(self.data['title'], self.data['rules']) +
            "Подтвердите, вы приняли препарат?"
        )
        self.send_ws_data({
            'token': self.objectStorage.token,
            'request_type': 'is_sent',
            'measurement_id': self.data['id'],
        })
        self.current_input_function = self.second_yes_no
        self.call_later_delay = 15
        self.call_later_on_end = True

    def second_yes_no(self, text):
        if self.is_positive(text):
            self.call_later_on_end = False
            self.send_ws_data({
                'token': self.objectStorage.token,
                'request_type': 'pushvalue',
                'value': self.data['title'],
            })
            self.send_ws_data({
                'token': self.objectStorage.token,
                'request_type': 'is_done',
                'measurement_id': self.data['id'],
            })
            self.objectStorage.play_speech.play("Отлично!", cache=True)
        elif self.is_negative(text):
            self.objectStorage.play_speech.play("Хотите отложить напоминание на 15 минут?", cache=True)
            self.call_later_delay = 15
            self.call_later_yes_no_fail_text = "Подтвердите прием позже с помощью комманды 'какие лекарства " \
                                               "необходимо принять' "
            self.current_input_function = self.call_later_yes_no
            self.need_permanent_answer = True
        else:
            self.objectStorage.play_speech.play("Извините, я вас не очень поняла", cache=True)

    current_input_function = first
    name = 'Уведомление о принятии лекарства'


class MedicineNotificationEvent(Event, ABC):
    name = "Уведомление о лекарствах"

    async def loop_item(self):
        await self.web_socket_connect(
            'medicines/',
            {
                "token": self.object_storage.token,
                "request_type": "init"
            },
        )

    async def return_dialog(self, dialog_engine_instance):
        self.dialog_class = MedicineNotificationDialog
        return await self.get_dialog(self.object_storage, self.data, self.ws, dialog_engine_instance)
