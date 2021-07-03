from events.event import EventDialog
import requests
import logging


class MessageNotificationDialog(EventDialog):
    def _loop_item(self):
        try:
            answer = requests.get(
                self.objectStorage.host+'/speakerapi/incomingmessage/',
                json={
                    'token': self.objectStorage.token,
                    'last_messages': False
                }
            )
            if answer.status_code != 200:
                logging.error(
                    "Error with getting data from server. Status code: "
                    "{}. Answer: {}".format(
                        answer.status_code, answer.text[:100]))
                return
        except requests.exceptions.ConnectTimeout:
            logging.error(
                "Error with getting data from server! Timeout.")
            return

        answer = answer.json()
        if answer == []:
            return

        self.text = answer[0]["fields"]["text"]
        self.event_happend = True
        logging.debug("Got message from server: {}".format(self.text))

    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Вам пришло новое сообщение, "+self.text)

    cur = first
    name = 'Уведомление о новом сообщении'
