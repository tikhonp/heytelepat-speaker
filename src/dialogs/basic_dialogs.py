import datetime
import locale
import logging
import random
import sys
import time

import pymorphy2
import requests
from bs4 import BeautifulSoup

try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning("RPi.GPIO is not available, button is disabled")

from dialogs import Dialog
from init_gates.config_gate import save_config

try:
    import alsaaudio
except ImportError:
    logging.warning(
        "AlsaAudio import error, make sure development mode is active")
    alsaaudio = None

try:
    locale.setlocale(locale.LC_TIME, "ru_RU.utf8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "ru_RU")


class TimeDialog(Dialog):
    def first(self, _):
        str_formatted_time = datetime.datetime.now().astimezone().strftime(
            "%A, %-d %B, %H:%M")
        str_formatted_time = "Сейчас " + str_formatted_time + "."
        self.objectStorage.play_speech.play(str_formatted_time)

    current_input_function = first
    name = 'Время'
    keywords = ['время', 'который']


class SetVolumeDialog(Dialog):
    def first(self, _):
        if alsaaudio is None:
            return
        self.objectStorage.play_speech.play(
            "Какую громкость вы хотите поставить?", cache=True)
        self.current_input_function = self.second
        self.need_permanent_answer = True

    def second(self, text):
        if not (value := self.to_integer(text)):
            self.objectStorage.play_speech.play(
                "Необходимо указать числовое значение.", cache=True)
            return

        if value < 1 or value > 300:
            self.objectStorage.play_speech.play(
                "Необходимо значение в промежутке от 1 до 300.", cache=True)
            return

        m = alsaaudio.Mixer(control='Speaker', cardindex=1)
        m.setvolume(value)

        self.objectStorage.play_speech.play(
            "Громкость установлена.", cache=True)

    current_input_function = first
    name = 'Громкость'
    keywords = ['громкость']


class HelpDialog(Dialog):
    def first(self, _):
        self.objectStorage.play_speech.play(
            "Я знаю очень много вещей, например 'который час' и умею общаться с вашим врачом. "
            "Попросите меня отправить сообщение врачу или спросите: "
            "'Расскажи о непрочитанных сообщениях', и я прочитаю новые сообщения от врача. "
            "Я напомню о необходимых опросниках, которые нужно направить врачу, "
            "а если вы пропустите просто попросите: 'Заполнить опросники.' "
            "Если вам нужно передать только одно измерение произнесите: 'Записать значение измерения.' "
            "Чтобы не забыть о лекарствах, спросите 'Какие лекарства мне нужно принять?', "
            "А чтобы подтвердить прием лекарства скажите 'Подтверди прием.'", cache=True
        )

    current_input_function = first
    name = 'Помощь'
    keywords = ['умеешь']


class ResetDialog(Dialog):
    last_time_pressed = None
    count_presses = 0
    button_pin = 17
    time_delay = 1.1

    def callback(self, _):
        current_time = int(time.time())
        if self.last_time_pressed is None:
            self.count_presses = 1
            self.last_time_pressed = current_time
        elif (current_time - self.last_time_pressed) < self.time_delay:
            self.count_presses += 1
            self.last_time_pressed = current_time
        else:
            self.count_presses = 0

    def reset_speaker(self):
        self.objectStorage.play_speech.play("Восстанавливаю заводские настройки.", cache=True)
        if self.fetch_data(
                'delete',
                self.objectStorage.host_http + 'speaker/',
                json={'token': self.objectStorage.token}
        ) is None:
            return
        config = self.objectStorage.config
        config['token'] = None
        save_config(config, self.objectStorage.config_filename)
        self.objectStorage.play_speech.play("Успешно восстановлены заводские настройки.", cache=True)
        sys.exit()

    def first(self, _):
        if self.objectStorage.development:
            return self.reset_speaker()
        self.objectStorage.play_speech.play(
            "Для поддтверждения сброса колонки нажмите трижды на кнопку или один раз для отмены.", cache=True
        )
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING, callback=self.callback, bouncetime=250)
        while True:
            if self.count_presses >= 3:
                return self.reset_speaker()
            if self.last_time_pressed and self.count_presses == 1 and \
                    (int(time.time()) - self.last_time_pressed) > self.time_delay:
                GPIO.remove_event_detect(self.button_pin)
                self.objectStorage.play_speech.play(
                    "Отменено.", cache=True
                )
                return

    current_input_function = first
    name = 'Сброс до заводских настроек'
    keywords = ['сброс', 'заводск']


class AnekDialog(Dialog):
    @staticmethod
    def get_anek():
        answer = requests.get('https://baneks.ru/random')
        if not answer.ok:
            logging.error("Error load anek connection, {}, {}".format(answer.status_code, answer.text[:100]))
            return

        return BeautifulSoup(answer.text, 'html.parser').find_all('meta', attrs={'name': 'description'})[0]["content"]

    def first(self, _):
        if anek := self.get_anek():
            self.objectStorage.play_speech.play(anek)
        else:
            self.objectStorage.play_speech.play("Ошибка соединения с сервером.", cache=True)

    current_input_function = first
    name = "Анекдот"
    keywords = ["анек"]


class WeatherDialog(Dialog):
    def get_weather_data(self):
        payload = {
            'q': self.objectStorage.city, 'appid': self.objectStorage.weather_token, 'lang': 'RU', 'units': 'metric'
        }
        answer = requests.get('https://api.openweathermap.org/data/2.5/weather', params=payload)
        if answer.ok:
            return answer.json()

    def generate_phrase(self):
        if not (weather_data := self.get_weather_data()):
            return
        morph = pymorphy2.MorphAnalyzer()

        city = morph.parse(weather_data.get('name'))[0].inflect({'loct'}).word
        int_degrees = int(weather_data.get('main', {}).get('temp'))
        degrees = morph.parse('градус')[0].make_agree_with_number(int_degrees).word
        int_degrees_max = int(weather_data.get('main', {}).get('temp_max'))
        degrees_max = morph.parse('градус')[0].make_agree_with_number(int_degrees_max).word
        description = weather_data.get('weather')[0].get('description')

        return "В {city} сейчас {description}, {int_degrees} ".format(
            city=city, description=description, int_degrees=int_degrees
        ) + "{degrees}, максимальная температура воздуха сегодня {int_degrees_max} {degrees_max}.".format(
            degrees=degrees, int_degrees_max=int_degrees_max, degrees_max=degrees_max
        )

    def first(self, _):
        if phrase := self.generate_phrase():
            self.objectStorage.play_speech.play(phrase)
        else:
            self.objectStorage.play_speech.play("Ошибка соединения с сервером.", cache=True)

    current_input_function = first
    name = "Погода"
    keywords = ['погод']


class HowAreYouDialog(Dialog):
    answers = [
        'Лучше всех!', 'По тихой грусти.', 'Всё ок!', 'Нормально.',
        'Спасибо - все хорошо - а у вас? — очень приятно - до свидания.',
        'Ничего', 'Чего только ни…', 'Эх, какие у нас дела? У нас делишки, а ДЕЛА у прокурора',
        'Да пока живу, и вроде умирать не собираюсь', 'Пенсия хорошая. повысили.',
        'Зарплата хорошая. Маленькая, но хорошая.', 'Просто так', 'Что, так просто?', 'Все пучком', 'Как в «Брат 2»',
        'Отлично! Чего и вам желаю', 'Все хорошо, а будет еще лучше!', 'Лучше всех. Хорошо, что никто не завидует.',
        'Отлично, не дождётесь.', 'Хорошо — не поверишь, плохо — не поможешь', 'Поцелуй меня сперва!',
        'Вчера сломал два ребра…', 'Как сажа бела', 'Как в сказке', 'Как всегда, то есть хорошо',
        'Как всегда, то есть плохо', 'C точки зрения банальной эрудиции игнорирую критерии утопического субъективизма, '
                                     'концептуально интерпретируя общепринятые дефанизирующие поляризаторы, поэтому '
                                     'консенсус, достигнутый диалектической материальной классификацией всеобщих'''
                                     ' мотиваций в парадогматических связях предикатов, решает проблему'
                                     ' усовершенствования формирующих геотрансплантационных квазипузлистатов всех '
                                     'кинетически коррелирующих аспектов, а так нормально.',
        'Хорово', 'Как у тебя.', 'Как в Польше: у кого телега тот и пан', 'Какие, собственно, дела?', 'Как всегда',
        'Как видишь', 'Ещё жива.', 'Окей', 'Не умер и не женился', 'Нет никаких дел',
        'Какие дела? Я не при делах нынче!', 'Ах я бедный-несчастный, так устал, мне каждый день приходится придумывать'
                                             ' ответ на вопрос «Как дела?»',
        'Старушенция Агата Кристи однажды сказала замечательную фразу: «Не обязательно что-то говорить, '
        'если нечего сказать».', 'Есть два способа поставить человека в тупик: спросить у него «Как дела» и попросить'
                                 ' рассказать что-нибудь', 'Не знаю', 'Дела идут, контора пишет',
        'Относительно. Если сравнивать с Лениным — то хорошо, если с миллионером — то не очень.', 'В среднем по району',
        'Пока еще никого не загрызла', 'Завидуйте молча', 'Задай другой вопрос пожалуйста',
        'Мне тоже всё равно, как у тебя дела, но так как мы с тобой давно не виделись, из приличия'
        ' надо что-то спросить.', 'Да нормально, вчера нобелевскую премию получила за вклад в развитие экоструктурных '
                                  'подразделений в области китообразных инфузорий туфелек и тапочек и за открытие '
                                  'нано-технологий, которые помогут пингвинам преодолеть ледниковый период в'
                                  ' африканских борах и гавайских пустынях в штате Масса Чуссетс округ Вашингтон.',
        'Вы несравненно оригинальны в своих вопросах'
    ]

    def first(self, _):
        self.objectStorage.play_speech.play(random.choice(self.answers), cache=True)

    current_input_function = first
    name = "Как дела"
    keywords = [('как', 'дела'), ('как', 'ты')]
