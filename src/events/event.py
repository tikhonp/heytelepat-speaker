import datetime
import json
import logging
from threading import Thread

import websockets


class Event(Thread):
    """Provides attributes and methods for event using in event engine."""

    event_happened = False
    dialog_class = None

    def __init__(self, object_storage):
        """
        :param ObjectStorage object_storage: ObjectStorage instance
        """
        Thread.__init__(self)

        self.objectStorage = object_storage
        self.ws = None
        logging.debug("Creating EventDialog '{}'".format(self.name))

    def on_message(self, msg: str):
        """Default message handler"""

        logging.warning("Default websocket message handler handled '{}'".format(msg))

    async def web_socket_connect(self, url, data_json, on_message):
        """Creates websocket, stores it in `Event.ws` and sends data `data_json`

        :param string url: url to connect without domain
        :param Union[dict, list] data_json: json serializable data to send to socket
        :param function on_message:  function that handles message with one parameter `msg`
        """
        url = self.objectStorage.host_ws + url

        # noinspection PyUnresolvedReferences
        try:
            async with websockets.connect(url) as self.ws:
                await self.ws.send(json.dumps(data_json))
                while True:
                    msg = await self.ws.recv()
                    on_message(msg)

        except websockets.exceptions.ConnectionClosedError:
            return None

    def _loop_item(self):
        """You must provide ._loop_item method if using default .run()"""

        raise NotImplementedError("You must provide ._loop_item() method if using default .run()")

    def run(self):
        """Default run method for loop running ._loop_item()"""

        logging.debug("Running EventDialog '{}'".format(self.name))
        while not self.event_happened:
            self._loop_item()
            self.objectStorage.event_obj.wait(5)

    def get_dialog(self, *args, **kwargs):
        """Default get dialog method, that implements getting dialog on event happened"""

        if self.dialog_class is None:
            raise NotImplementedError("You must provide dialog class")
        return self.dialog_class(*args, **kwargs)

    def return_dialog(self, *args, **kwargs):
        """You must provide return dialog method"""

        raise NotImplementedError("You must provide return dialog method")

    @staticmethod
    def get_time_dialog():
        """You must provide return dialog method and then override it"""

        return False


class EventsEngine(Thread):
    def __init__(self, object_storage, events_dialog_list, dialog_engine_instance):
        super().__init__()
        self.objectStorage = object_storage
        self.eventsDialogList = events_dialog_list
        self.runningEvents = list()
        self.timeDialogs = list()
        self.dialogEngineInstance = dialog_engine_instance
        logging.info("Creating events engine Thread with %d events", len(events_dialog_list))

    def _put_dialog_to_time(self, datetime_dialog, dialog):
        self.timeDialogs.append(
            (datetime_dialog.timestamp(), dialog))

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
            self.timeDialogs.pop(i)

    def _run_item(self):
        for event in self.runningEvents:
            if event.event_happened:
                self.dialogEngineInstance.add_dialog_to_queue(
                    event.return_dialog())
                event.event_happened = False

            if time_dialog := event.get_time_dialog():
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
