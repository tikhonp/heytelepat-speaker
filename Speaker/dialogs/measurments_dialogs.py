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
            [('пульс'), {
                "id": 1,
                "name": "pulse",
                "description": "Пульс в покое",
                "unit": "удары в минуту",
                "type": "integer",
                "default_representation": "scatter",
                "is_legacy": False,
                "subcategory": "Измерения"
            }],
        ]

        self.category = None
        for i in categories:
            for phrase in i[0]:
                if phrase in _input.lower():
                    self.category = i[1]

        if self.category is None:
            self.objectStorage.speak.play(
                "Категория нераспознана, "
                "пожалуйста, назовите категорию еще раз", cashed=True)
            self.cur = self.second
            return

        answer = requests.get(
            self.objectStorage.host+'/speakerapi/getlistcategories/',
            json={
                'token': self.objectStorage.token,
                'names_only': True
            })
        if answer.status_code == 200:
            if self.category not in answer.json():
                self.objectStorage.speakSpeech.play(
                    "Эта категория не поддерживается для этого пользователя",
                    cashed=True)
                return
        else:
            self.objectStorage.speakSpeech.play(
                "Ошибка соединения с сервером", cashed=True)
            logging.error("Message send err {} {}".format(
                    answer, answer.text[:100]))
            return

        self.objectStorage.play(
            "Произнесите значение", cashed=True)
        self.cur = self.third
        self.need_permanent_answer = True

    def third(self, _input):
        if self.category["type"] == "integer":
            if not _input.is_digit():
                self.objectStorage.speakSpeech.play(
                    "Значение не распознано, пожалуйста,"
                    " произнесите его еще раз", cashed=True)
            value = int(_input)
        else:
            logging.error("Unknown type %s" % self.category["type"])
            return

        answer = requests.post(
            self.objectStorage.host+'/speakerapi/pushvalue/',
            json={
                'token': self.objectStorage.token,
                'data': [{
                    'category_name': self.category["pulse"],
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
