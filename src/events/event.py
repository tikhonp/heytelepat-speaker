import asyncio
import json
import logging

import websockets


class Event:
    """Provides attributes and methods for event using in event engine."""

    def __init__(self, object_storage, loop):
        """
        :param init_gates.config_gate.ObjectStorage object_storage: ObjectStorage instance
        :param asyncio.AbstractEventLoop loop: Asyncio event asyncio_loop
        :return: __init__ should return None
        :rtype: None
        """

        self.event_happened = False
        self.dialog_class = None
        self.object_storage = object_storage
        self.ws = None
        self.stop = False
        self.loop = loop
        self.data = None
        logging.debug("Creating EventDialog '{}'".format(self.get_name))

    async def on_message(self, message):
        """Default async message handler

        :param dict | list message: Data with message from server
        :rtype: None
        """

        logging.debug("Default websocket message handler handled '{}'".format(message))
        self.data = message
        self.event_happened = True

    async def kill(self):
        """Kill event async"""

        self.stop = True

    async def web_socket_connect(self, url, data_json, on_message=None):
        """Creates websocket, stores it in `Event.ws` and sends data `data_json` (async)

        :param string data_json: Json serializable string data to send after connect
        :param string url: url to connect without domain :param dict data_json: json serializable data to send to
        socket
        :param function on_message:  async function that handles message with one parameter `msg`,
        default `.on_message()`
        :rtype: None
        """

        url = self.object_storage.host_ws + url

        try:
            async with websockets.connect(url) as self.ws:
                await self.ws.send(json.dumps(data_json))
                while True:
                    if message := self.decode_json(await self.ws.recv()):
                        if on_message:
                            await on_message(message)
                        else:
                            await self.on_message(message)
        except websockets.exceptions.ConnectionClosedError:
            return

    async def loop_item(self):
        """Async function that uses in asyncio_loop"""

        raise NotImplementedError("You must provide `.loop_item()` method if using default `.run()`.")

    async def run(self):
        """Default async run method for asyncio_loop running `.loop_item()`"""

        logging.debug("Running EventDialog '{}'".format(self.get_name))

        task = self.loop.create_task(self.loop_item())
        while True:
            if task.done():
                task = self.loop.create_task(self.loop_item())
            if self.stop:
                if not task.cancelled():
                    task.cancel()
                break
            await asyncio.sleep(2)

    async def get_dialog(self, *args, **kwargs):
        """Default get dialog method, that implements getting dialog on event happened"""

        if not self.event_happened:
            raise RuntimeError("You can't call `.get_dialog()` if not `.happened`.")

        if self.dialog_class is None:
            raise NotImplementedError("You must provide dialog class")

        return self.dialog_class(*args, **kwargs)

    async def return_dialog(self):
        """Get complete dialog instance

        :return: Dialog Instance
        :rtype: dialogs.dialog.Dialog
        """

        raise NotImplementedError("You must provide `.return_dialog()` method if using default `.run()`.")

    @property
    def get_name(self):
        """Name of event.

        :rtype: string
        """

        if hasattr(self, 'name'):
            return str(self.name)
        else:
            return 'Base Event'

    @staticmethod
    def decode_json(data):
        """Decode data to python dict

        :param string data: Json serializable string
        :return: Python object from data
        :rtype: dict | list
        """

        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            logging.error("Error decoding message '%s'", data)
            return


class EventsEngine:
    """Provides async methods for run lifecycle of event's."""

    def __init__(self, object_storage, events_dialog_list, dialog_engine_instance, loop):
        """
        :param init_gates.config_gate.ObjectStorage object_storage: ObjectStorage instance
        :param list[Event] events_dialog_list: List of events classes to run
        :param dialogs.dialog.DialogEngine dialog_engine_instance: DialogEngine instance
        :param asyncio.AbstractEventLoop loop: Asyncio event asyncio_loop
        :return: __init__ should return None
        :rtype: None
        """

        self.object_storage = object_storage
        self.events_dialog_list = events_dialog_list
        self.dialog_engine_instance = dialog_engine_instance
        self.loop = loop

        self.stop = False
        self.running_events = list()  # list of tuples [(`Event instance`, `running task`)]

        logging.info("Creating events engine with %d events", len(events_dialog_list))

    async def kill(self):
        """Kill event async"""

        self.stop = True

    async def _put_event_to_running(self, event):
        """Initialise event and put it to events list.

        :param Event event: Event class
        """

        e = event(self.object_storage, self.loop)
        task = self.loop.create_task(e.run())
        self.running_events.append((e, task))

    async def _first_run(self):
        """Initialise all events."""

        for event in self.events_dialog_list:
            await self._put_event_to_running(event)

    async def _run_item(self):
        """Async method to run single item of running events iteration"""

        for event, t in self.running_events:
            if event.event_happened:
                self.dialog_engine_instance.add_dialog_to_queue(
                    await event.return_dialog())
                event.event_happened = False

    async def _stop_events(self):
        """Run kill() on all events."""

        tasks = list()
        for event, t in self.running_events:
            await event.kill()
            tasks.append(t)

        await asyncio.gather(*tasks)

    async def run(self):
        """Async method runs events engine initialises events and provides it's lifecycle."""

        logging.info("Starting events engine.")
        await self._first_run()

        while True:
            try:
                await self._run_item()
            except Exception as e:
                logging.error("There is error in event engine: %s", e)
                if self.object_storage.debug_mode or self.object_storage.development:
                    raise e

            if self.stop:
                await self._stop_events()
                break

            await asyncio.sleep(1)
