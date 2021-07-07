from dialogs.dialog import Dialog
import logging
import requests
import datetime


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
            answer = requests.post(
                self.objectStorage.host+"/speakerapi/getlistcategories/",
                json={
                    'token': self.objectStorage.token,
                    'message': self.message,
                })

            if answer.status_code == 200:
                text = "Сообщение успешно отправлено!"
            else:
                text = "Произошла ошибка приотправлении сообщения"
                logging.error("Message send err {} {}".format(
                    answer, answer.text[:100]))

            self.objectStorage.speakSpeech.play(text, cashed=True)

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
        answer = requests.get(
            self.objectStorage.host+'/speakerapi/incomingmessage/',
            json={
                'token': self.objectStorage.token,
                'last_messages': True
            })

        if answer.status_code != 200:
            self.objectStorage.speakSpeech.play(
                "Произошла ошибка при загрузке сообщений", cashed=True)
            logging.error("Message send err {} {}".format(
                    answer, answer.text))
            return

        answer = answer.json()

        if len(answer) == 0:
            self.objectStorage.speakSpeech.play(
                "Новых сообщений нет", cashed=True)
            return

        for i in answer:
            date = datetime.datetime.strptime(
                i['fields']['date'], "%Y-%m-%dT%H:%M:%SZ")
            date_str = date.astimezone().strftime(
                "%A, %-d %B, %H:%M")

            text = "Сообщение. От {}. {}".format(
                date_str, i['fields']['text'])
            self.objectStorage.speakSpeech.play(text)
            self.objectStorage.event_obj.wait(0.5)

    cur = first
    name = 'Непрочитанные сообщения'
    keywords = ['непрочитан', 'нов']
