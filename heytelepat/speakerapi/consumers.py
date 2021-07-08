from channels.generic.websocket import WebsocketConsumer
import time


class WSTest(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(10):
            self.send("something {}".format(i))
            time.sleep(5)
