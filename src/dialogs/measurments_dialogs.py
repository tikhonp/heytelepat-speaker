import asyncio
import json
import logging

from dialogs.dialog import Dialog

categories = [
    [['пульс'], {
        "id": 1,
        "name": "pulse",
        "description": "Пульс в покое",
        "unit": "удары в минуту",
        "request_type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения"
    }],
]
dry_categories = [
    {
        "id": 30,
        "name": "symptom",
        "description": "Симптом заболевания",
        "unit": "",
        "request_type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 31,
        "name": "action",
        "description": "Действие",
        "unit": "",
        "request_type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 19,
        "name": "waist_circumference",
        "description": "Окружность талии",
        "unit": "см",
        "request_type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 3,
        "name": "diastolic_pressure",
        "description": "Диастолическое (нижнее) артериальное давление",
        "unit": "мм рт. ст.",
        "request_type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 1,
        "name": "pulse",
        "description": "Пульс в покое",
        "unit": "удары в минуту",
        "request_type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 4,
        "name": "weight",
        "description": "Вес",
        "unit": "кг",
        "request_type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 5,
        "name": "height",
        "description": "Рост",
        "unit": "см",
        "request_type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 2,
        "name": "systolic_pressure",
        "description": "Систолическое (верхнее) артериальное давление в покое",
        "unit": "мм рт. ст.",
        "request_type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 25,
        "name": "temperature",
        "description": "Температура",
        "unit": "град Цельсия",
        "request_type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 24,
        "name": "glukose",
        "description": "Глюкоза",
        "unit": "моль/литр",
        "request_type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 23,
        "name": "pain_assessment",
        "description": "Оценка боли",
        "unit": "балл(а)(ов)",
        "request_type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Ощущения",
    },
    {
        "id": 21,
        "name": "leg_circumference_right",
        "description": "Обхват правой голени",
        "unit": "см",
        "request_type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 29,
        "name": "medicine",
        "description": "Принятое лекарство",
        "unit": "",
        "request_type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 20,
        "name": "leg_circumference_left",
        "description": "Обхват левой голени",
        "unit": "см",
        "request_type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 22,
        "name": "spo2",
        "description": "Насыщение крови кислородом",
        "unit": "%",
        "request_type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 32,
        "name": "side_effect",
        "description": "Побочный эффект",
        "unit": "",
        "request_type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 33,
        "name": "health",
        "description": "Субъективное самочувствие",
        "unit": "",
        "request_type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Ощущения",
    },
    {
        "id": 34,
        "name": "activity",
        "description": "Физическая активность",
        "unit": "минуты",
        "request_type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 35,
        "name": "information",
        "description": "Общая информация",
        "unit": "",
        "request_type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 36,
        "name": "steps",
        "description": "Количество пройденных шагов",
        "unit": "шаги",
        "request_type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Данные с мобильных устройств",
    },
    {
        "id": 37,
        "name": "glukose_fasting",
        "description": "Глюкоза натощак",
        "unit": "ммоль/л",
        "request_type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Эндокринология",
    },
    {
        "id": 38,
        "name": "peak_flow",
        "description": "Предельная скорость выдоха",
        "unit": "л/мин",
        "request_type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Пульмонология",
    },
]


class AddValueDialog(Dialog):
    category = None

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            "Какое значение вы хотите отправить?", cache=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, text):
        self.category = None
        text = text.lower()

        for i in categories:
            for phrase in i[0]:
                if phrase in text:
                    self.category = i[1]
                    break
            if self.category is not None:
                break

        if self.category is None:
            for i in dry_categories:
                keys = i['description'].strip().lower().split()
                for k in keys:
                    if k in text:
                        self.category = i
                        break
                if self.category is not None:
                    break

        if self.category is None:
            self.objectStorage.speakSpeach.play(
                "Категория нераспознана, "
                "пожалуйста, назовите категорию еще раз", cache=True)
            self.cur = self.second
            return

        self.objectStorage.speakSpeech.play(
            "Произнесите значение", cache=True)
        self.cur = self.third
        self.need_permanent_answer = True

    def third(self, text):
        type_m = self.category.get('request_type', '') \
                 + self.category.get('value_type', '')
        if type_m == "integer":
            value = self.to_integer(text)
        elif type_m == "float":
            value = self.to_float(text)
        elif type_m == 'textarea':
            value = text
            if self.category.get('category', '') == 'information':
                if text.strip().lower() == 'нет':
                    value = ''
            if prefix := self.category.get('prefix', False):
                value = prefix + ' ' + value
        else:
            logging.error("Unknown request_type %s" % self.category["request_type"])
            return

        if value is None:
            self.objectStorage.speakSpeech.play(
                "Значение не распознано, пожалуйста,"
                " произнесите его еще раз", cache=True)
            return

        if self.fetch_data(
                'post',
                self.objectStorage.host_http + 'measurement/push/',
                json={
                    'token': self.objectStorage.token,
                    'values': [{
                        'category_name': self.category.get('name', '')
                                         + self.category.get('category', ''),
                        'value': value
                    }]
                }):
            self.objectStorage.speakSpeech.play(
                "Значение успешно отправлено.", cache=True)

        if hasattr(self, 'data') and len(self.data['fields']) > 0:
            return self.yes_no('да')
        if hasattr(self, 'ws'):
            self.loop.create_task(
                self.ws.send(json.dumps({
                    'token': self.objectStorage.token,
                    'request_type': 'is_done',
                    'measurement_id': self.data['id'],
                })))

    cur = first
    name = 'Отправить значение измерения'
    keywords = ['измерени', 'значени']


class CommitFormsDialog(Dialog):
    data = None
    current = None
    category = None

    def first(self, text):
        if answer := self.fetch_data(
                'get',
                self.objectStorage.host_http + 'measurement/',
                json={
                    'token': self.objectStorage.token,
                    'request_type': 'get'
                }):

            self.data = answer
            self.first_t(text)
        elif isinstance(answer, list):
            self.objectStorage.speakSpeech.play(
                "Нет незаплоненных опросников", cache=True)

    def first_t(self, text):
        if hasattr(self, 'current'):
            self.fetch_data(
                'patch',
                self.objectStorage.host_http + 'measurement/',
                json={
                    'token': self.objectStorage.token,
                    'request_type': 'is_done',
                    'measurement_id': self.current['id']
                })

        if self.data:
            self.current = self.data.pop(0)
            self.objectStorage.speakSpeech.play(
                self.current['patient_description']
                + " Вы готовы произнести ответ сейчас?")
            if not self.current['is_sent']:
                self.fetch_data(
                    'patch',
                    self.objectStorage.host_http + 'measurement/',
                    json={
                        'token': self.objectStorage.token,
                        'request_type': 'is_sent',
                        'measurement_id': self.current['id']
                    })
            self.cur = self.yes_no
            self.need_permanent_answer = True
        else:
            self.objectStorage.speakSpeech.play(
                "Спасибо за заполнение опросника", cache=True)

    def yes_no(self, text):
        if self.is_positive(text):
            self.category = self.current['fields'].pop(0)
            self.objectStorage.speakSpeech.play(
                "Произнесите значение {}".format(self.category.get('text')))
            self.cur = self.third
            self.need_permanent_answer = True
            return
        elif self.is_negative(text):
            self.objectStorage.speakSpeech.play(
                "Введите значение позже с помощию"
                " команды 'запистать значение'", cache=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Извините, я вас не очень поняла", cashe=True
            )

    def third(self, text):
        type_m = self.category.get('request_type', '') \
                 + self.category.get('value_type', '')
        if type_m == "integer":
            value = self.to_integer(text)
        elif type_m == "float":
            value = self.to_float(text)
        elif type_m == 'textarea':
            value = text
            if self.category.get('category', '') == 'information':
                if text.strip().lower() == 'нет':
                    value = ''
            if prefix := self.category.get('prefix', False):
                value = prefix + ' ' + value
        else:
            logging.error("Unknown request_type %s" % self.category["request_type"])
            return

        if value is None:
            self.objectStorage.speakSpeech.play(
                "Значение не распознано, пожалуйста,"
                " произнесите его еще раз", cache=True)
            return

        if self.fetch_data(
                'post',
                self.objectStorage.host_http + 'measurement/push/',
                json={
                    'token': self.objectStorage.token,
                    'values': [{
                        'category_name': self.category.get('name', '')
                                         + self.category.get('category', ''),
                        'value': value
                    }]
                }):
            self.objectStorage.speakSpeech.play(
                "Значение успешно отправлено.", cache=True)

        if len(self.current['fields']) > 0:
            return self.yes_no('да')
        else:
            return self.first_t(text)

    cur = first
    name = 'Заполнить незаполненные опросники'
    keywords = ['заполни', 'опросник']
