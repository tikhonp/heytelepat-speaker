from threading import Thread
import logging
import websockets
import json


class EventDialog(Thread):
    event_happend = False
    dialog_class = None

    def __init__(self, objectStorage):
        Thread.__init__(self)

        self.objectStorage = objectStorage
        logging.debug("Creating EventDialog '{}'".format(self.name))

    async def webSocketConnect(self, url, data_json, on_message, port=8001):
        url = 'ws://{}:{}/{}'.format(
            self.objectStorage.host.split('/')[2], port, url)

        try:
            async with websockets.connect(url) as self.ws:
                await self.ws.send(json.dumps(data_json))
                while True:
                    msg = await self.ws.recv()
                    on_message(msg)

        except websockets.exceptions.ConnectionClosedError:
            return None

    def run(self):
        logging.debug("Running EventDialog '{}'".format(self.name))
        while not self.event_happend:
            self._loop_item()
            self.objectStorage.event_obj.wait(5)

    def get_dialog(self, *args, **kwargs):
        if self.dialog_class is None:
            raise NotImplementedError("You must provide dialog class")
        return self.dialog_class(*args, **kwargs)

    def return_dialog(self, *args, **kwargs):
        raise NotImplementedError("You must provide return dialog method")


class EventsEngine(Thread):
    def __init__(self, objectStorage, eventsDialogList, dialogEngineInstance):
        super().__init__()
        self.objectStorage = objectStorage
        self.eventsDialogList = eventsDialogList
        self.runningEvents = []
        self.dialogEngineInstance = dialogEngineInstance
        logging.info("Creating events engine Thread")

    def _first_run(self):
        for event in self.eventsDialogList:
            e = event(self.objectStorage)
            e.start()
            self.runningEvents.append(e)

    def _run_item(self):
        for event in self.runningEvents:
            if event.event_happend:
                self.dialogEngineInstance.add_dialog_to_queue(
                    event.return_dialog())
                event.event_happend = False

    def run(self):
        logging.info("Starting events engine Thread")
        self._first_run()

        while True:
            try:
                self._run_item()
            except Exception as e:
                logging.error("There is error in event engine: %s", e)
                if self.objectStorage.debug_mode:
                    raise e
