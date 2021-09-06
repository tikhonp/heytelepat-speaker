import asyncio
import logging
import struct

import aioconsole
import pyaudio

try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning("RPi.GPIO is not available, button is disabled")
try:
    import pvporcupine
except ImportError:
    logging.warning("pvporcupine is not available, required -d mode")


async def wakeup_word_input_function(_, k=2, sensitivity=0.6, async_delay=0.1):
    keywords = [
        'alexa', 'bumblebee', 'computer', 'hey google', 'hey siri',
        'jarvis', 'picovoice', 'porcupine', 'terminator'
    ]
    keyword = keywords[k]

    porcupine = pvporcupine.create(keywords=[keyword], sensitivities=[sensitivity])

    pa = None
    audio_stream = None

    try:
        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)

        logging.info("Listening wake up word '{}'...".format(keyword))

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                break
            await asyncio.sleep(async_delay)
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        porcupine.delete()


# noinspection PyUnusedLocal
async def raspberry_input_function(loop, gpio_pin=17, async_delay=0.1):
    """Async raspberrypi input button

    :param asyncio.AbstractEventLoop loop: Asyncio event asyncio_loop
    :param integer gpio_pin: Pin which button connected to
    :param async_delay: Delay in seconds that button updates
    :return: None
    :rtype: None
    """

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.IN, GPIO.PUD_UP)

    logging.info("Waiting button...")
    while True:
        if GPIO.input(gpio_pin) == GPIO.LOW:
            logging.info("Button was pushed!")
            return
        await asyncio.sleep(async_delay)


# noinspection PyUnusedLocal
async def async_simple_input_function(loop, phrase="Press enter and tell something! "):
    """Async equivalent of `input()`

    :param asyncio.AbstractEventLoop loop: Asyncio event asyncio_loop
    :param string phrase: Phrase that will be printed before input
    :return: Inputted string
    :rtype: string
    """

    return await aioconsole.ainput(phrase)


class SoundProcessor:
    """Processes sound input and waits for user input."""

    def __init__(self, object_storage, dialog_engine_instance):
        """
        :param init_gates.ObjectStorage object_storage: ObjectStorage instance
        :param dialogs.dialog.DialogEngine dialog_engine_instance: DialogEngine instance
        :return: __init__ should return None
        :rtype: None
        """

        self.object_storage = object_storage
        self.dialog_engine_instance = dialog_engine_instance

        self.stop = False

        logging.info("Created SoundProcessor engine")

    async def kill(self):
        """Kill event async"""

        self.stop = True

    def _get_voice_sr(self):
        text = self.object_storage.listen_recognize_speech.listen()

        if text is None:
            self.object_storage.play_speech.play(
                "Я не расслышал, повторите, пожалуйста еще. Перед ответом нажмите на кнопку.", cache=True)
            return

        return text

    async def _run_item(self):
        """Process sound input"""

        self.object_storage.pixels.wakeup()
        text = await self.object_storage.event_loop.run_in_executor(
            None, self._get_voice_sr
        )

        if text is not None:
            if await self.object_storage.event_loop.run_in_executor(
                    None, lambda t=text: self.dialog_engine_instance.process_input(t)
            ):
                await self._run_item()

    async def run(self):
        """Main async run function provides waiting for user input and handles voice."""

        logging.info("Started soundProcessorInstance")

        input_func_task = self.object_storage.event_loop.create_task(
            self.object_storage.inputFunction(self.object_storage.event_loop)
        )
        run_item_task = None

        while True:
            if input_func_task and input_func_task.done():
                run_item_task = self.object_storage.event_loop.create_task(self._run_item())
                input_func_task = None
            if run_item_task and run_item_task.done():
                input_func_task = self.object_storage.event_loop.create_task(
                    self.object_storage.inputFunction(self.object_storage.event_loop)
                )
                run_item_task = None

            if self.stop:
                if input_func_task and not input_func_task.cancelled():
                    input_func_task.cancel()
                if run_item_task and not run_item_task.cancelled():
                    run_item_task.cancel()
                break

            await asyncio.sleep(1)
