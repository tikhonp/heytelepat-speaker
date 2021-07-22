from dateutil import parser
from dialogs.dialog import Dialog


class SendMessageDialog(Dialog):
    message = None

    def first(self, text):
        self.objectStorage.speakSpeech.play(
            "Какое сообщение вы хотите отправить?", cache=True)
        self.cur = self.get_message
        self.need_permanent_answer = True

    def get_message(self, text):
        self.objectStorage.speakSpeech.play(
            "Вы написали: " + text + ". Отправить сообщение?")
        self.cur = self.submit
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
                self.objectStorage.speakSpeech.play(
                    "Сообщение успешно отправлено!", cache=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Хотите продиктовать сообщение повторно?", cache=True)
            self.cur = self.repeat
            self.need_permanent_answer = True

    def repeat(self, text):
        if self.is_positive(text):
            return self.first(text)
        elif not self.is_negative(text):
            self.objectStorage.speakSpeech.play(
                "Извините, я вас не очень поняла", cashe=True
            )

    cur = first
    name = 'Отправить Сообщение'
    keywords = ['отправ', 'сообщение']


class NewMessagesDialog(Dialog):
    def first(self, text):
        if (answer := self.fetch_data(
                'get',
                self.objectStorage.host_http + 'message/',
                json={
                    'token': self.objectStorage.token,
                })) is None:
            return

        if not answer:
            self.objectStorage.speakSpeech.play(
                "Новых сообщений нет", cache=True)
            return

        for i in answer:
            date = parser.parse(i.get('date'))
            date_str = date.astimezone().strftime(
                "%A, %-d %B, %H:%M")

            text = "{} - {} - написал: - {}".format(
                i.get('sender'), date_str, i.get('text')
            )
            self.objectStorage.speakSpeech.play(text)
            self.objectStorage.event_obj.wait(0.5)

    cur = first
    name = 'Непрочитанные сообщения'
    keywords = ['непрочитан', 'нов']
