import asyncio
import functools
import json
import logging

import websockets

from dialogs.dialog import Dialog


class EventDialog(Dialog):
    """Expand dialog for events usage"""

    def __init__(self, object_storage, data, ws, loop, dialog_engine_instance):
        """
        :param ObjectStorage object_storage: ObjectStorage instance
        :param object data: Python object data to use in dialog
        :param websockets.legacy.client.WebSocketClientProtocol ws: Websocket instance
        :param asyncio.AbstractEventLoop loop: Asyncio event asyncio_loop
        :param dialogs.dialog.DialogEngine dialog_engine_instance: DialogEngine instance
        :return: __init__ should return None
        :rtype: None
        """

        super().__init__(object_storage)

        self.data = data
        self.ws = ws
        self.loop = loop
        self.dialog_engine_instance = dialog_engine_instance

        self.call_later_delay = None
        self.call_later_yes_no_fail_text = None

        self.call_later_on_end = False

    def send_ws_data(self, data):
        """Send data with websocket

        :param dict | list data: Json serializable python object
        :return: Nothing
        :rtype: None
        """

        self.loop.create_task(
            self.ws.send(
                json.dumps(data)
            )
        )

    def call_dialog_later(self, delay, dialog):
        """Call `dialog_engine_instance.add_dialog_to_queue` with given dialog instance after given number of seconds

        :param int | float delay: Number of minutes that will be called add dialog
        :param dialogs.dialog.Dialog dialog: Instance if dialog
        :return: An instance of `asyncio.TimerHandle` is returned which can be used to cancel the callback
        :rtype: asyncio.TimerHandle
        """

        return self.loop.call_later(delay * 60, self.dialog_engine_instance.add_dialog_to_queue, dialog)

    def call_later_yes_no(self, text):
        """Dialog engine function handles yes/no/null input and calls `.call_dialog_later()` if yes
        with number of minutes delay in `.self.call_later_delay` (int or float)
        with fail text in `.call_later_yes_no_fail_text` (string)

        :param string text: Default dialog engine param
        :return: None
        :rtype: None
        """

        if self.call_later_delay is None:
            raise NotImplementedError("To call `.call_later_yes_no()` you must pass delay into `.call_later_delay`.")
        elif not isinstance(self.call_later_delay, (int, float)):
            raise ValueError(
                "`.call_later_delay` must be `int` or `float`, but got `{}`".format(type(self.call_later_delay))
            )

        if self.call_later_yes_no_fail_text is None:
            raise NotImplementedError(
                "To call `.call_later_yes_no()` you must pass fail text into `.call_later_yes_no_fail_text`."
            )
        elif not isinstance(self.call_later_yes_no_fail_text, str):
            raise ValueError(
                "`.call_later_yes_no_fail_text` must be `str`, but got `{}`".format(
                    type(self.call_later_yes_no_fail_text))
            )

        if self.is_positive(text):
            dialog = self.__class__(self.objectStorage, self.data, self.ws, self.loop, self.dialog_engine_instance)
            self.call_dialog_later(self.call_later_delay, dialog)
            self.objectStorage.speakSpeech.play("Напомню через {} минут.".format(self.call_later_delay))
            self.call_later_delay = False
        elif self.is_negative(text):
            self.objectStorage.speakSpeech.play(self.call_later_yes_no_fail_text, cache=True)
        else:
            self.objectStorage.speakSpeech.play("Извините, я вас не очень поняла", cashe=True)

    def __del__(self):
        if self.call_later_on_end:
            if self.call_later_delay is None:
                raise NotImplementedError(
                    "To call `.call_later_yes_no()` you must pass delay into `.call_later_delay`.")
            elif not isinstance(self.call_later_delay, (int, float)):
                raise ValueError(
                    "`.call_later_delay` must be `int` or `float`, but got `{}`".format(type(self.call_later_delay))
                )

            dialog = self.__class__(self.objectStorage, self.data, self.ws, self.loop, self.dialog_engine_instance)
            self.call_dialog_later(self.call_later_delay, dialog)


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

        :param dict | list data_json: Json serializable python object data to send after connect
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

        loop_item_task = self.loop.create_task(self.loop_item())

        while True:
            if loop_item_task.done():
                loop_item_task = self.loop.create_task(self.loop_item())

            if self.stop:
                if not loop_item_task.cancelled():
                    loop_item_task.cancel()
                if self.ws:
                    await self.ws.close()
                break

            await asyncio.sleep(2)

    async def get_dialog(self, *args, **kwargs):
        """Default get dialog method, that implements getting dialog on event happened

        :return: DialogEvent Instance
        :rtype: EventDialog
        """

        if not self.event_happened:
            raise RuntimeError("You can't call `.get_dialog()` if not `.happened`.")

        if self.dialog_class is None:
            raise NotImplementedError("You must provide dialog class")

        return self.dialog_class(*args, **kwargs)

    async def return_dialog(self, dialog_engine_instance):
        """Get complete dialog instance

        :param dialogs.dialog.DialogEngine dialog_engine_instance: DialogEngine instance
        :return: Dialog Instance
        :rtype: dialogs.dialog.Dialog
        """

        raise NotImplementedError("You must provide `.return_dialog()` method if using default `.run()`.")

    @functools.cached_property
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

    def __init__(self, object_storage, events_dialog_list, dialog_engine_instance):
        """
        :param init_gates.config_gate.ObjectStorage object_storage: ObjectStorage instance
        :param list[Event] events_dialog_list: List of events classes to run
        :param dialogs.dialog.DialogEngine dialog_engine_instance: DialogEngine instance
        :return: __init__ should return None
        :rtype: None
        """

        self.object_storage = object_storage
        self.events_dialog_list = events_dialog_list
        self.dialog_engine_instance = dialog_engine_instance
        self.loop = object_storage.event_loop

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
                    await event.return_dialog(self.dialog_engine_instance))
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
            await self._run_item()

            if self.stop:
                await self._stop_events()
                break

            await asyncio.sleep(1)
