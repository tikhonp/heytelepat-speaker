from threading import Thread
import logging
import websockets
import json
import datetime


class EventDialog(Thread):
    event_happend = False
    dialog_class = None

    def __init__(self, objectStorage):
        Thread.__init__(self)

        self.objectStorage = objectStorage
        logging.debug("Creating EventDialog '{}'".format(self.name))

    async def webSocketConnect(self, url, data_json, on_message):
        url = 'ws://{}/{}'.format(
            self.objectStorage.host.split('/')[2], url)

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

    def get_time_dialog(self):
        return False


class EventsEngine(Thread):
    def __init__(self, objectStorage, eventsDialogList, dialogEngineInstance):
        super().__init__()
        self.objectStorage = objectStorage
        self.eventsDialogList = eventsDialogList
        self.runningEvents = list()
        self.timeDialogs = list()
        self.dialogEngineInstance = dialogEngineInstance
        logging.info("Creating events engine Thread")

    def _put_dialog_to_time(self, datetime, dialog):
        self.timeEvents.append(
            (datetime.timestamp(), dialog))

    def _put_event_to_running(self, event):
        e = event(self.objectStorage)
        e.start()
        self.runningEvents.append(e)

    def _first_run(self):
        for event in self.eventsDialogList:
            self._put_event_to_running(event)

    def _run_time_item(self):
        to_delete = list()
        now = datetime.datetime.now().timestamp()
        for i, dialog_time in enumerate(self.timeDialogs):
            if now >= dialog_time[0]:
                self.dialogEngineInstance.add_dialog_to_queue(
                    dialog_time[1])
                to_delete.append(i)

        for i in to_delete:
            self.dialog_time.pop(i)

    def _run_item(self):
        for event in self.runningEvents:
            if event.event_happend:
                self.dialogEngineInstance.add_dialog_to_queue(
                    event.return_dialog())
                event.event_happend = False

            if (time_dialog := event.get_time_dialog()):
                self._put_dialog_to_time(*time_dialog)

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
            try:
                self._run_time_item()
            except Exception as e:
                logging.error(
                    "There is error in dialog time in event engine: %s", e)
                if self.objectStorage.debug_mode:
                    raise e
