from dialogs.dialog import Dialog
import requests
import logging


class AddValueDialog(Dialog):
    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Какое значение вы хотите отправить?", cashed=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, _input):
        categories = [
            [('кровь'), '']
        ]

        self.category = None
        for i in categories:
            for phrase in i[0]:
                if phrase in _input.lower():
                    self.category = i[0]

        if self.category is None:
            self.objectStorage.speak.play(
                "Категория нераспознана, "
                "пожалуйста, назовите категорию еще раз", cashed=True)
            self.cur = self.second
            return

        self.objectStorage.play(
            "Произнесите значение", cashed=True)
        self.cur = self.third
        self.need_permanent_answer = True

    def third(self, _input):
        if not _input.is_digit():
            self.objectStorage.speakSpeech.play(
                "Значение не распознано, пожалуйста,"
                " произнесите его еще раз", cashed=True)

        value = int(_input)

        answer = requests.post(
            self.objectStorage.host+'/speakerapi/pushvalue/',
            json={
                'token': self.objectStorage.token,
                'data': [{
                    'category_name': self.category,
                    'value': value
                }]
            })

        if answer.status_code == 200:
            text = "Значение успешно отправлено."
        else:
            text = "Произошла ошибка при отправлении значения"
            logging.error("Value send err {} {}".format(
                answer, answer.text[:100]))

        self.objectStorage.speakSpeech.play(text, cashed=True)

    cur = first
    name = 'Отправить значение измерения'
    keywords = ['измерени', 'значени']
