import pymorphy2
from dateutil import parser

from dialogs import Dialog


class SendMessageDialog(Dialog):
    message = None

    def first(self, _):
        self.objectStorage.play_speech.play(
            "Какое сообщение вы хотите отправить?", cache=True)
        self.current_input_function = self.get_message
        self.need_permanent_answer = True

    def get_message(self, text):
        self.objectStorage.play_speech.play(
            "Вы написали: " + text + ". Отправить сообщение?")
        self.current_input_function = self.submit
        self.message = text.title()
        self.need_permanent_answer = True

    def submit(self, text):
        if self.is_positive(text):
            if self.fetch_data(
                    'post',
                    self.objectStorage.host_http + "message/send/",
                    json={
                        'token': self.objectStorage.token,
                        'message': self.message,
                    }):
                self.objectStorage.play_speech.play(
                    "Сообщение успешно отправлено!", cache=True)
        else:
            self.objectStorage.play_speech.play(
                "Хотите продиктовать сообщение повторно?", cache=True)
            self.current_input_function = self.repeat
            self.need_permanent_answer = True

    def repeat(self, text):
        if self.is_positive(text):
            return self.first(text)
        elif not self.is_negative(text):
            self.objectStorage.play_speech.play(
                "Извините, я вас не очень поняла", cache=True
            )

    current_input_function = first
    name = 'Отправить Сообщение'
    keywords = [('отправ', 'сообщение'), 'сообщение']


class NewMessagesDialog(Dialog):
    def first(self, _):
        if (answer := self.fetch_data(
                'get',
                self.objectStorage.host_http + 'message/',
                json={
                    'token': self.objectStorage.token,
                })) is None:
            return

        if not answer:
            self.objectStorage.play_speech.play(
                "Новых сообщений нет.", cache=True)
            return

        morph = pymorphy2.MorphAnalyzer()

        for i in answer:
            date = parser.parse(i.get('date'))
            date_str = date.astimezone().strftime('%-d %B, %H:%M')
            week_day = morph.parse(
                date.astimezone().strftime('%A')
            )[0].inflect({'accs'}).word

            text = "{sender} - в {week_day}, {date_str} - написал: - {text}".format(
                sender=i.get('sender'), week_day=week_day, date_str=date_str, text=i.get('text')
            )
            self.objectStorage.play_speech.play(text)

    current_input_function = first
    name = 'Непрочитанные сообщения'
    keywords = ['непрочитан', 'нов']
