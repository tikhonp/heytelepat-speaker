from dialogs.dialog import Dialog
from dateutil import parser


class SendMessageDialog(Dialog):
    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Какое сообщение вы хотите отправить?", cashed=True)
        self.cur = self.get_message
        self.need_permanent_answer = True

    def get_message(self, _input):
        self.objectStorage.speakSpeech.play(
            "Вы написали: " + _input + ". Отправить сообщение?")
        self.cur = self.submit
        self.message = _input
        self.need_permanent_answer = True

    def submit(self, _input):
        text = _input.lower().strip()
        if 'да' in text:
            if self.fetch_data(
                    'post',
                    self.objectStorage.host+"/speakerapi/sendmessage/",
                    json={
                        'token': self.objectStorage.token,
                        'message': self.message,
                    }):

                self.objectStorage.speakSpeech.play(
                    "Сообщение успешно отправлено!", cashed=True)
        else:
            self.objectStorage.speakSpeech.play(
                "Хотите продиктовать сообщение повторно?", cashed=True)
            self.cur = self.repeat
            self.need_permanent_answer = True

    def repeat(self, _input):
        text = _input.lower().strip()
        if 'да' in text:
            return self.first(_input)

    cur = first
    name = 'Отправить Сообщение'
    keywords = ['отправ', 'сообщение']


class NewMessagesDialog(Dialog):
    def first(self, _input):
        if (answer := self.fetch_data(
                    'get',
                    self.objectStorage.host+'/speakerapi/incomingmessage/',
                    json={
                        'token': self.objectStorage.token,
                    })) is None:
            return

        if not answer:
            self.objectStorage.speakSpeech.play(
                "Новых сообщений нет", cashed=True)
            return

        for i in answer:
            date = parser.parse(i['date'])
            date_str = date.astimezone().strftime(
                "%A, %-d %B, %H:%M")

            text = "Сообщение. От {}. {}".format(
                date_str, i['text'])
            self.objectStorage.speakSpeech.play(text)
            self.objectStorage.event_obj.wait(0.5)

    cur = first
    name = 'Непрочитанные сообщения'
    keywords = ['непрочитан', 'нов']
