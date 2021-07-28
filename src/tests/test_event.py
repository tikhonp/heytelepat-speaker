import asyncio
import os
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from events.event import Event
from init_gates.config_gate import ObjectStorage, load_config
from dialogs.dialog import Dialog

config_file_path = os.path.join(Path.home(), '.speaker/config.json')
config = load_config(config_file_path)


class TestEventGeneric(IsolatedAsyncioTestCase):
    def setUp(self):
        self.object_storage = ObjectStorage(config, development=True)
        self.event = Event(self.object_storage)

    async def test_on_message(self):
        await self.event.on_message('hello')

    async def test_get_dialog_raise_runtime(self):
        with self.assertRaises(RuntimeError):
            await self.event.get_dialog()

    async def test_get_dialog_raise_not_implemented(self):
        self.event.event_happened = True
        with self.assertRaises(NotImplementedError):
            await self.event.get_dialog()

    async def test_get_dialog(self):
        self.event.event_happened = True
        dialog = Dialog
        self.event.dialog_class = dialog
        self.assertIsInstance(await self.event.get_dialog(self.object_storage), dialog)

    async def test_kill(self):
        await self.event.kill()
        self.assertEqual(self.event.stop, True)

    async def test__loop_item(self):
        with self.assertRaises(NotImplementedError):
            await self.event.loop_item()


# class TestEventWebSocketConnect(TestCase, TestEvent):
#     def test_web_socket_connect(self):
#         self.fail()


class TestEventRun(IsolatedAsyncioTestCase):
    def setUp(self):
        object_storage = ObjectStorage(config, development=True)
        self.event = Event(object_storage)

    # async def test_run_fails(self):
    #     with self.assertRaises(NotImplementedError):
    #         await self.event.run(asyncio.get_event_loop())

    # async def test_run(self):
    #     async def _loop_item(self):
    #         pass
    #
    #     self.event._loop_item = _loop_item
    #     asyncio_loop = asyncio.get_event_loop()
    #     task = asyncio_loop.create_task(self.event.run(asyncio_loop))
    #     await self.event.kill()
    #     await task
