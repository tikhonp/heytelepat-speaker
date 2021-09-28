from dialogs import Dialog


class CheckMedicinesDialog(Dialog):
    current = None
    data = None

    def first(self, text):
        if answer := self.fetch_data(
                'get',
                self.objectStorage.host_http + 'medicine/',
                json={
                    'token': self.objectStorage.token,
                    'request_type': 'get'
                }):

            self.data = answer
            self.first_t(text)
        elif isinstance(answer, list):
            self.objectStorage.play_speech.play(
                "Нет препаратов которые необходимо принять.", cache=True)

    def first_t(self, _):
        if self.data:
            self.current = self.data.pop(0)
            self.objectStorage.play_speech.play(
                "Вам необходимо принять препарат {}. {}. ".format(self.current['title'], self.current['rules']) +
                "Подтвердите, вы приняли препарат?"
            )
            if not self.current['is_sent']:
                self.commit_medicine_status('is_sent')
            self.current_input_function = self.yes_no
            self.need_permanent_answer = True
        else:
            self.objectStorage.play_speech.play(
                "Спасибо за заполнение уведомление о выпитых препаратах.", cache=True
            )

    def commit_medicine_status(self, request_type: str):
        self.fetch_data(
            'patch',
            self.objectStorage.host_http + 'medicine/',
            json={
                'token': self.objectStorage.token,
                'request_type': request_type,
                'measurement_id': self.current.get('id')
            })

    def yes_no(self, text):
        if self.is_positive(text):
            self.fetch_data(
                'post',
                self.objectStorage.host_http + 'medicine/commit/',
                json={
                    "token": self.objectStorage.token,
                    "medicine": self.current.get('title')
                }
            )
            self.commit_medicine_status('is_done')
            self.objectStorage.play_speech.play("Отлично!", cache=True)
            return self.first_t(text)
        elif self.is_negative(text):
            self.objectStorage.play_speech.play(
                "Подтвердите прием позже с помощью комманды 'какие лекарства необходимо принять'.", cache=True
            )
        else:
            self.objectStorage.play_speech.play(
                "Извините, я вас не очень понял.", cache=True
            )

    current_input_function = first
    name = 'Неприятные лекарства'
    keywords = [('лекарств', 'принят'), ('препарат', 'принят')]


class CommitMedicineDialog(Dialog):
    def first(self, _):
        self.objectStorage.play_speech.play(
            "Какое лекарство вы приняли?", cache=True
        )
        self.current_input_function = self.second
        self.need_permanent_answer = True

    def second(self, text):
        value = text
        if self.fetch_data(
                'post',
                self.objectStorage.host_http + 'medicine/commit/',
                json={
                    "token": self.objectStorage.token,
                    "medicine": value
                }):
            self.objectStorage.play_speech.play(
                "Отлично, лекарство {} отмечено.".format(value)
            )

    current_input_function = first
    name = 'Подтверждение лекарства'
    keywords = [('подтверд', 'лекарств'), ('приня')]
