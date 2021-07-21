from dialogs.dialog import Dialog


class CheckMedicinesDialog(Dialog):
    current = None
    data = None

    def first(self, _input):
        if answer := self.fetch_data(
                'get',
                self.objectStorage.host+'/speakerapi/medicine/',
                json={
                    "token": self.objectStorage.token,
                    "request_type": "get"
                }):

            self.data = answer
            self.first_t(_input)
        elif isinstance(answer, list):
            self.objectStorage.speakSpeech.play(
                "Нет препаратов которые необходимо принять", cashed=True)

    def first_t(self, _input):
        if self.data:
            self.current = self.data.pop(0)
            self.objectStorage.speakSpeech.play(
                "Вам необходимо принять препарат {}. {}. ".format(self.current['title'], self.current['rules']) +
                "Подтвердите, вы приняли препарат?"
            )
            if not self.current['is_sent']:
                self.commit_medicine_status('is_sent')
            self.cur = self.yes_no
            self.need_permanent_answer = True
        else:
            self.objectStorage.speakSpeech.play(
                "Спасибо за заполнение уведомление о выпитых препаратах", cashed=True
            )

    def commit_medicine_status(self, type: str):
        self.fetch_data(
            'patch',
            self.objectStorage.host + '/speakerapi/medicine/',
            json={
                'token': self.objectStorage.token,
                'request_type': type,
                'measurement_id': self.current.get('id')
            })

    def yes_no(self, _input):
        if 'да' in _input.lower():
            self.fetch_data(
                'post',
                self.objectStorage.host+'/speakerapi/medicine/commit/',
                json={
                    "token": self.objectStorage.token,
                    "medicine": self.current.get('title')
                }
            )
            self.commit_medicine_status('is_done')
            self.objectStorage.speakSpeech.play("Отлично!", cashed=True)
            return self.first_t(_input)
        else:
            self.objectStorage.speakSpeech.play(
                "Подтвердите прием позже с помощью комманды 'какие лекарства необходимо принять'", cashed=True
            )

    cur = first
    name = 'Неприятные лекарства'
    keywords = ['лекарств', 'препарат', 'принят']


class CommitMedicineDialog(Dialog):
    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Какое лекарство вы приняли?", cashed=True
        )
        self.cur = self.yes_no
        self.need_permanent_answer = True

    def yes_no(self, _input):
        value = _input.strip()
        if self.fetch_data(
                'post',
                self.objectStorage.host+'/speakerapi/medicine/commit/',
                json={
                    "token": self.objectStorage.token,
                    "medicine": value
                }):
            self.objectStorage.speakSpeech.play(
                "Отлично, лекарство {} отмечено".format(value)
            )

    cur = first
    name = 'Подтверждение лекарства'
    keywords = ['подтверд', 'лекарств']