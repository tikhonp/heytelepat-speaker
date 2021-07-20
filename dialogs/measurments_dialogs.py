from dialogs.dialog import Dialog
import logging
import asyncio
import json


categories = [
    [['пульс'], {
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
dry_categories = [
    {
        "id": 30,
        "name": "symptom",
        "description": "Симптом заболевания",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 31,
        "name": "action",
        "description": "Действие",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 19,
        "name": "waist_circumference",
        "description": "Окружность талии",
        "unit": "см",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 3,
        "name": "diastolic_pressure",
        "description": "Диастолическое (нижнее) артериальное давление",
        "unit": "мм рт. ст.",
        "type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 1,
        "name": "pulse",
        "description": "Пульс в покое",
        "unit": "удары в минуту",
        "type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 4,
        "name": "weight",
        "description": "Вес",
        "unit": "кг",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 5,
        "name": "height",
        "description": "Рост",
        "unit": "см",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 2,
        "name": "systolic_pressure",
        "description": "Систолическое (верхнее) артериальное давление в покое",
        "unit": "мм рт. ст.",
        "type": "integer",
        "default_representation": "scatter",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 25,
        "name": "temperature",
        "description": "Температура",
        "unit": "град Цельсия",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 24,
        "name": "glukose",
        "description": "Глюкоза",
        "unit": "моль/литр",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 23,
        "name": "pain_assessment",
        "description": "Оценка боли",
        "unit": "балл(а)(ов)",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Ощущения",
    },
    {
        "id": 21,
        "name": "leg_circumference_right",
        "description": "Обхват правой голени",
        "unit": "см",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 29,
        "name": "medicine",
        "description": "Принятое лекарство",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 20,
        "name": "leg_circumference_left",
        "description": "Обхват левой голени",
        "unit": "см",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 22,
        "name": "spo2",
        "description": "Насыщение крови кислородом",
        "unit": "%",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Измерения",
    },
    {
        "id": 32,
        "name": "side_effect",
        "description": "Побочный эффект",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 33,
        "name": "health",
        "description": "Субъективное самочувствие",
        "unit": "",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Ощущения",
    },
    {
        "id": 34,
        "name": "activity",
        "description": "Физическая активность",
        "unit": "минуты",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 35,
        "name": "information",
        "description": "Общая информация",
        "unit": "",
        "type": "string",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Общее",
    },
    {
        "id": 36,
        "name": "steps",
        "description": "Количество пройденных шагов",
        "unit": "шаги",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Данные с мобильных устройств",
    },
    {
        "id": 37,
        "name": "glukose_fasting",
        "description": "Глюкоза натощак",
        "unit": "ммоль/л",
        "type": "float",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Эндокринология",
    },
    {
        "id": 38,
        "name": "peak_flow",
        "description": "Предельная скорость выдоха",
        "unit": "л/мин",
        "type": "integer",
        "default_representation": "values",
        "is_legacy": False,
        "subcategory": "Пульмонология",
    },
]


class AddValueDialog(Dialog):
    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Какое значение вы хотите отправить?", cashed=True)
        self.cur = self.second
        self.need_permanent_answer = True

    def second(self, _input):
        self.category = None
        text = _input.lower()

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
            self.objectStorage.speak.play(
                "Категория нераспознана, "
                "пожалуйста, назовите категорию еще раз", cashed=True)
            self.cur = self.second
            return

        self.objectStorage.speakSpeech.play(
            "Произнесите значение", cashed=True)
        self.cur = self.third
        self.need_permanent_answer = True

    def third(self, _input):
        type_m = self.category.get('type', '') \
            + self.category.get('value_type', '')
        if type_m == "integer":
            if not _input.isdigit():
                self.objectStorage.speakSpeech.play(
                    "Значение не распознано, пожалуйста,"
                    " произнесите его еще раз", cashed=True)
                return
        elif type_m == "float":
            if _input.isdigit():
                value = int(_input)
            elif 'и' in _input.lower():
                d = [i.strip() for i in _input.lower().split('и')]
                if sum([i.isdigit() for i in d]) and len(d) == 2:
                    value = float(".".join(d))
                else:
                    self.objectStorage.speakSpeech.play(
                        "Значение не распознано, пожалуйста,"
                        " произнесите его еще раз", cashed=True)
        elif type_m == 'textarea':
            value = _input.strip()
            if self.category.get('category', '') == 'information':
                if _input.strip().lower() == 'нет':
                    value = ''
            if prefix := self.category.get('prefix', False):
                value = prefix + ' ' + value
        else:
            logging.error("Unknown type %s" % self.category["type"])
            return

        if value is not None:
            if self.fetch_data(
                    'post',
                    self.objectStorage.host+'/speakerapi/pushvalue/',
                    json={
                        'token': self.objectStorage.token,
                        'values': [{
                            'category_name': self.category.get('name', '')
                            + self.category.get('category', ''),
                            'value': value
                        }]
                    }):
                self.objectStorage.speakSpeech.play(
                    "Значение успешно отправлено.", cashed=True)

        if hasattr(self, 'data') and len(self.data['fields']) > 0:
            return self.yes_no('да')
        if hasattr(self, 'ws'):
            asyncio.new_event_loop().run_until_complete(
                self.ws.send(json.dumps({
                    'token': self.objectStorage.token,
                    'request_type': 'is_done',
                    'measurement_id': self.data['id'],
                })))

    cur = first
    name = 'Отправить значение измерения'
    keywords = ['измерени', 'значени']


class CommitFormsDialog(Dialog):
    def first(self, _input):
        if answer := self.fetch_data(
                'get',
                self.objectStorage.host+'/speakerapi/measurements/',
                json={
                    'token': self.objectStorage.token,
                    'request_type': 'get'
                }):
            if len(answer) == 0:
                self.objectStorage.speakSpeech.play(
                    "Нет незаплоненных опросников", cashed=True)
                return

            self.data = answer
            self.first_t(_input)

    def first_t(self, _input):
        if hasattr(self, 'current'):
            self.fetch_data(
                'patch',
                self.objectStorage.host+'/speakerapi/measurements/',
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
                    self.objectStorage.host+'/speakerapi/measurements/',
                    json={
                        'token': self.objectStorage.token,
                        'request_type': 'is_sent',
                        'measurement_id': self.current['id']
                    })
            self.cur = self.yes_no
            self.need_permanent_answer = True
        else:
            self.objectStorage.speakSpeech.play(
                "Спасибо за заполнение опросника", cashed=True)

    def yes_no(self, _input):
        if 'да' in _input.lower():
            self.category = self.current['fields'].pop(0)
            self.objectStorage.speakSpeech.play(
                "Произнесите значение {}".format(self.category.get('text')))
            self.cur = self.third
            self.need_permanent_answer = True
            return
        else:
            self.objectStorage.speakSpeech.play(
                "Введите значение позже с помощию"
                " команды 'запистать значение'", cashed=True)

    def third(self, _input):
        type_m = self.category.get('type', '') \
            + self.category.get('value_type', '')
        if type_m == "integer":
            if not _input.isdigit():
                self.objectStorage.speakSpeech.play(
                    "Значение не распознано, пожалуйста,"
                    " произнесите его еще раз", cashed=True)
                return
        elif type_m == "float":
            if _input.isdigit():
                value = int(_input)
            elif 'и' in _input.lower():
                d = [i.strip() for i in _input.lower().split('и')]
                if sum([i.isdigit() for i in d]) and len(d) == 2:
                    value = float(".".join(d))
                else:
                    self.objectStorage.speakSpeech.play(
                        "Значение не распознано, пожалуйста,"
                        " произнесите его еще раз", cashed=True)
        elif type_m == 'textarea':
            value = _input.strip()
            if self.category.get('category', '') == 'information':
                if _input.strip().lower() == 'нет':
                    value = None
            if prefix := self.category.get('prefix', False):
                value = prefix + ' ' + value
        else:
            logging.error("Unknown type %s" % self.category["type"])
            return

        if value is not None:
            if self.fetch_data(
                    'post',
                    self.objectStorage.host+'/speakerapi/pushvalue/',
                    json={
                        'token': self.objectStorage.token,
                        'values': [{
                            'category_name': self.category.get('name', '')
                            + self.category.get('category', ''),
                            'value': value
                        }]
                    }):
                self.objectStorage.speakSpeech.play(
                    "Значение успешно отправлено.", cashed=True)

        if len(self.current['fields']) > 0:
            return self.yes_no('да')
        else:
            return self.first_t(_input)

    cur = first
    name = 'Заполнить незаполненные опросники'
    keywords = ['заполни', 'опросник']
