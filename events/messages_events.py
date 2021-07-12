from events.event import EventDialog
import logging
import json
import asyncio


class MessageNotificationDialog(EventDialog):
    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        answer = None
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while answer is None:
            answer = asyncio.get_event_loop().run_until_complete(
                self.webSocketConnect(
                    'ws/speakerapi/incomingmessage/',
                    {
                        "token": self.objectStorage.token,
                        "last_messages": False
                    }
                ))

        answer = json.loads(answer)
        self.text = answer[0]["fields"]["text"]
        self.event_happend = True

    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Вам пришло новое сообщение, "+self.text)

    cur = first
    name = 'Уведомление о новом сообщении'
