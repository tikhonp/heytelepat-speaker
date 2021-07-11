from events.event import EventDialog
import requests
import logging
import json
import websockets
import asyncio


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

    async def webSocketConnect(self, port=8001):
        url = 'ws://{}:{}/ws/speakerapi/incomingmessage/'.format(
            self.objectStorage.host.split('/')[2], str(port))

        try:
            async with websockets.connect(url) as ws:
                await ws.send(json.dumps({
                    'token': self.objectStorage.token,
                    'last_messages': False
                }))
                msg = await ws.recv()
                return msg
        except websockets.exceptions.ConnectionClosedError:
            return None

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        answer = None
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while answer is None:
            answer = asyncio.get_event_loop().run_until_complete(
                self.webSocketConnect())

        answer = json.loads(answer)
        self.text = answer[0]["fields"]["text"]
        self.event_happend = True

    def first(self, _input):
        self.objectStorage.speakSpeech.play(
            "Вам пришло новое сообщение, "+self.text)

    cur = first
    name = 'Уведомление о новом сообщении'
