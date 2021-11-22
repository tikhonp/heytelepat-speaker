import json
import logging

from dialogs import Dialog

categories = [
    [['пульс', 'средеч'], {
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
    value = None

    def choose_category(self, text) -> bool:
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
            return False

        return True

    def first(self, text):
        if 'давлен' in text:
            return self.process_pressure_first(text)

        if self.choose_category(text):
            self.objectStorage.play_speech.play(
                "Произнесите значение", cache=True)
            self.current_input_function = self.third
        else:
            self.objectStorage.play_speech.play(
                "Какое измерение вы хотите отправить?", cache=True)
            self.current_input_function = self.second

        self.need_permanent_answer = True

    def second(self, text):
        self.category = None

        if 'давлен' in text:
            return self.process_pressure_first(text)

        if self.choose_category(text):
            self.objectStorage.play_speech.play(
                "Произнесите значение", cache=True)
            self.current_input_function = self.third
            self.need_permanent_answer = True
        else:
            self.objectStorage.play_speech.play(
                "Категория нераспознана, пожалуйста, назовите категорию еще раз", cache=True)
            self.current_input_function = self.second
            return

    def process_pressure_first(self, _):
        self.objectStorage.play_speech.play(
            "Пожалуйста, произнесите значение систолическое (верхнего) артериального давления в покое.", cache=True)
        self.current_input_function = self.process_pressure_second
        self.need_permanent_answer = True

    def process_pressure_second(self, text):
        value = self.to_integer(text)
        if value is None:
            self.objectStorage.play_speech.play(
                "Значение не распознано, пожалуйста,"
                " произнесите его еще раз", cache=True)
            self.current_input_function = self.process_pressure_second
            self.need_permanent_answer = True
            return

        if self.fetch_data(
                'post',
                self.objectStorage.host_http + 'measurement/push/',
                json={
                    'token': self.objectStorage.token,
                    'values': [{'category_name': 'systolic_pressure', 'value': value}]
                }):
            self.objectStorage.play_speech.play(
                "Значение успешно отправлено.", cache=True)

        self.objectStorage.play_speech.play(
            "Пожалуйста, произнесите значение, диастолического (нижнего) артериальное давления.", cache=True
        )
        self.current_input_function = self.process_pressure_third
        self.need_permanent_answer = True

    def process_pressure_third(self, text):
        value = self.to_integer(text)
        if value is None:
            self.objectStorage.play_speech.play(
                "Значение не распознано, пожалуйста,"
                " произнесите его еще раз", cache=True)
            self.current_input_function = self.process_pressure_third
            self.need_permanent_answer = True
            return

        if self.fetch_data(
                'post',
                self.objectStorage.host_http + 'measurement/push/',
                json={
                    'token': self.objectStorage.token,
                    'values': [{'category_name': 'diastolic_pressure', 'value': value}]
                }):
            self.objectStorage.play_speech.play(
                "Значение успешно отправлено.", cache=True)

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
                    self.value = value
                    return
            if prefix := self.category.get('prefix', False):
                value = prefix + ' ' + value
        else:
            logging.error("Unknown request_type %s" % self.category["request_type"])
            return

        if value is None:
            self.objectStorage.play_speech.play(
                "Значение не распознано, пожалуйста,"
                " произнесите его еще раз", cache=True)
            self.current_input_function = self.third
            self.need_permanent_answer = True
            return

        self.objectStorage.play_speech.play("Вы ввели - " + str(value) + ". Отправить значение?")
        self.value = value
        self.current_input_function = self.fourth
        self.need_permanent_answer = True

    def fourth(self, text):
        if self.is_positive(text):
            if self.fetch_data(
                    'post',
                    self.objectStorage.host_http + 'measurement/push/',
                    json={
                        'token': self.objectStorage.token,
                        'values': [{
                            'category_name': self.category.get('name', '') + self.category.get('category', ''),
                            'value': self.value
                        }]
                    }):
                self.objectStorage.play_speech.play(
                    "Значение успешно отправлено.", cache=True)

            if hasattr(self, 'data') and len(self.data['fields']) > 0:
                return self.yes_no('да')
            if hasattr(self, 'ws'):
                self.objectStorage.event_loop.create_task(
                    self.ws.send(json.dumps({
                        'token': self.objectStorage.token,
                        'request_type': 'is_done',
                        'measurement_id': self.data['id'],
                    })))
        elif self.is_negative(text):
            self.objectStorage.play_speech.play("Произнесите значение еще раз.", cache=True)
            self.value = None
            self.current_input_function = self.third
            self.need_permanent_answer = True
        else:
            self.objectStorage.play_speech.play(
                "Извините, я вас не очень понял. Записать значение {}?".format(str(self.value)), cache=True)
            self.current_input_function = self.fourth
            self.need_permanent_answer = True

    current_input_function = first
    name = 'Отправить значение измерения'
    keywords = ['измерени']


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
            self.objectStorage.play_speech.play(
                "Нет незаплоненных опросников", cache=True)

    def first_t(self, _):
        if self.current is not None:
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
            measurement_description = str(
                self.current.get('custom_text') or self.current.get('patient_description') or
                'Пожалуйста, произведите измерение ' + self.current.get('title')
            )
            self.objectStorage.play_speech.play(measurement_description + " Вы готовы произнести ответ сейчас?")

            if not self.current.get('is_sent'):
                self.fetch_data(
                    'patch',
                    self.objectStorage.host_http + 'measurement/',
                    json={
                        'token': self.objectStorage.token,
                        'request_type': 'is_sent',
                        'measurement_id': self.current['id']
                    })
            self.current_input_function = self.yes_no
            self.need_permanent_answer = True
        else:
            self.objectStorage.play_speech.play(
                "Спасибо за заполнение опросника", cache=True)

    def yes_no(self, text):
        if self.is_positive(text):
            self.category = self.current['fields'].pop(0)
            self.objectStorage.play_speech.play(
                "Произнесите значение {}".format(self.category.get('text')))
            self.current_input_function = self.third
            self.need_permanent_answer = True
            return
        elif self.is_negative(text):
            self.objectStorage.play_speech.play(
                "Введите значение позже с помощию"
                " команды 'запистать значение'", cache=True)
        else:
            self.objectStorage.play_speech.play(
                "Извините, я вас не очень понял", cache=True
            )
            self.current_input_function = self.yes_no
            self.need_permanent_answer = True
            return

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
            self.objectStorage.play_speech.play(
                "Значение не распознано, пожалуйста,"
                " произнесите его еще раз", cache=True)
            return

        if self.fetch_data(
                'post',
                self.objectStorage.host_http + 'measurement/push/',
                json={
                    'token': self.objectStorage.token,
                    'values': [{
                        'category_name': self.category.get('name', '') + self.category.get('category', ''),
                        'value': value
                    }]
                }):
            self.objectStorage.play_speech.play(
                "Значение успешно отправлено.", cache=True)

        if len(self.current['fields']) > 0:
            return self.yes_no('да')
        else:
            return self.first_t(text)

    current_input_function = first
    name = 'Заполнить незаполненные опросники'
    keywords = ['заполни', 'опросник']
